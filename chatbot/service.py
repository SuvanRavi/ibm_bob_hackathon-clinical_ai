"""
Chatbot Service
Main service for handling chatbot queries with LLM integration
"""

import json
import requests
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from .context import PatientContextRetriever, get_context_retriever
from .safety import SafetyValidator, get_safety_validator
from .templates import ResponseTemplates
from .config import (
    HF_API_TOKEN,
    HF_API_BASE_URL,
    PRIMARY_MODEL,
    FALLBACK_MODEL,
    MODEL_TEMPERATURE,
    MAX_TOKENS,
    REQUEST_TIMEOUT,
    MAX_RETRIES,
    RATE_LIMIT_DELAY,
    SYSTEM_PROMPT_MEDICAL,
    SYSTEM_PROMPT_GENERAL,
    ESCALATION_MESSAGE,
    MAX_CONVERSATION_LENGTH
)


class ChatbotService:
    """Main chatbot service with LLM integration"""
    
    def __init__(self):
        """Initialize chatbot service"""
        self.context_retriever = get_context_retriever()
        self.safety_validator = get_safety_validator()
        self.templates = ResponseTemplates()
        self.conversation_history: Dict[str, List[Dict]] = {}
        self.use_huggingface = self._check_huggingface_available()
        self.last_request_time = 0  # For rate limiting
    
    def _check_huggingface_available(self) -> bool:
        """Check if HuggingFace API is available and token is set"""
        # Re-read from environment at check time — this catches the case where
        # load_dotenv() in app.py ran AFTER config.py was first imported and
        # HF_API_TOKEN was captured as '' from the module-level assignment.
        import os
        token = os.environ.get('HF_API_TOKEN', '') or HF_API_TOKEN

        if not token:
            print("⚠️ HuggingFace API token not set. Using template-based responses.")
            print("   Fix: add HF_API_TOKEN=hf_xxxx to your .env file in the project root.")
            return False

        try:
            # Test API connectivity by sending an empty string or basic payload to the model endpoint via POST
            headers = {"Authorization": f"Bearer {token}"}
            payload = {"inputs": "ping"}
            
            response = requests.post(
                f"{HF_API_BASE_URL}/{PRIMARY_MODEL}",
                headers=headers,
                json=payload,
                timeout=5
            )
            
            # 200 means success, 503 means model is loading (token is valid)
            if response.status_code in [200, 503]:
                print("✓ HuggingFace API connected successfully")
                return True
            elif response.status_code == 401:
                print("⚠️ HuggingFace token is invalid or expired (401 Unauthorized).")
                print("   Fix: check your HF_API_TOKEN value at https://huggingface.co/settings/tokens")
                return False
            elif response.status_code == 403:
                print(f"⚠️ HuggingFace token does not have access to {PRIMARY_MODEL} (403 Forbidden).")
                print("   Fix: accept the model licence at https://huggingface.co/BioMistral/BioMistral-7B")
                return False
            else:
                print(f"⚠️ HuggingFace API returned status {response.status_code}. Using template-based responses.")
                return False
        except Exception as e:
            print(f"⚠️ HuggingFace API not available: {e}. Using template-based responses.")
            return False
    
    def process_query(
        self,
        patient_id: str,
        query: str,
        session_id: Optional[str] = None
    ) -> Dict:
        """
        Process user query and generate response
        
        Args:
            patient_id: Patient ID
            query: User's question
            session_id: Optional session ID for conversation history
            
        Returns:
            Response dictionary with answer and metadata
        """
        # Validate patient exists
        if not self.context_retriever.validate_patient_exists(patient_id):
            return {
                'success': False,
                'error': 'Patient not found',
                'message': 'Unable to retrieve patient information.'
            }
        
        # Validate query safety
        is_safe, error_message = self.safety_validator.validate_query(query)
        if not is_safe:
            return {
                'success': True,
                'response': error_message,
                'type': 'safety_block',
                'timestamp': datetime.now().isoformat()
            }
        
        # Get patient context
        patient_context = self.context_retriever.get_patient_context(patient_id)
        
        if not patient_context:
            return {
                'success': False,
                'error': 'Patient context unavailable',
                'message': 'Unable to retrieve patient medical information.'
            }
        
        # Classify query type
        query_type = self._classify_query(query)
        
        # Handle template-based responses for common queries
        template_response = self._try_template_response(query, query_type, patient_context)
        if template_response:
            return {
                'success': True,
                'response': template_response,
                'type': query_type,
                'source': 'template',
                'timestamp': datetime.now().isoformat()
            }
        
        # Generate LLM response
        if self.use_huggingface:
            response = self._generate_llm_response(
                query,
                patient_context,
                query_type,
                session_id
            )
        else:
            # Fallback to template-based response
            response = self._generate_fallback_response(query, query_type, patient_context)
        
        # Validate response safety
        is_safe, modified_response = self.safety_validator.validate_response(
            response,
            patient_context,
            confidence=0.8  # Default confidence for template responses
        )
        
        if not is_safe and modified_response:
            response = modified_response
        elif modified_response:
            response = modified_response
        
        # Store in conversation history
        if session_id and response:
            self._add_to_history(session_id, query, response)
        
        return {
            'success': True,
            'response': response,
            'type': query_type,
            'source': 'llm' if self.use_huggingface else 'fallback',
            'timestamp': datetime.now().isoformat()
        }
    
    def _classify_query(self, query: str) -> str:
        """
        Classify query type
        
        Args:
            query: User's query
            
        Returns:
            Query type string
        """
        query_lower = query.lower()
        
        # Medication queries
        if any(word in query_lower for word in ['medication', 'medicine', 'prescription', 'pill', 'drug', 'dose']):
            return 'medication'
        
        # Dietary queries
        if any(word in query_lower for word in ['food', 'eat', 'diet', 'nutrition', 'meal']):
            return 'dietary'
        
        # Appointment queries
        if any(word in query_lower for word in ['appointment', 'schedule', 'book', 'visit', 'consultation']):
            return 'appointment'
        
        # Allergy queries
        if any(word in query_lower for word in ['allergy', 'allergic', 'allergen']):
            return 'allergy'
        
        # Greeting
        if any(word in query_lower for word in ['hello', 'hi', 'hey', 'greetings']):
            return 'greeting'
        
        # Farewell
        if any(word in query_lower for word in ['bye', 'goodbye', 'thanks', 'thank you']):
            return 'farewell'
        
        return 'general'
    
    def _try_template_response(
        self,
        query: str,
        query_type: str,
        patient_context: Dict
    ) -> Optional[str]:
        """
        Try to generate response using templates
        
        Args:
            query: User's query
            query_type: Classified query type
            patient_context: Patient's medical context
            
        Returns:
            Template response or None
        """
        query_lower = query.lower()
        
        # Greeting
        if query_type == 'greeting':
            return self.templates.greeting(patient_context['patient_name'])
        
        # Farewell
        if query_type == 'farewell':
            return self.templates.farewell()
        
        # List medications
        if 'list' in query_lower and 'medication' in query_lower:
            return self.templates.medication_list(patient_context['prescriptions'])
        
        # Allergy information
        if query_type == 'allergy' or 'allerg' in query_lower:
            return self.templates.allergy_information(patient_context['allergies'])
        
        # Dietary advice
        if query_type == 'dietary' and 'should i eat' in query_lower:
            return self.templates.dietary_advice(
                patient_context['diagnosis'],
                patient_context['allergies']
            )
        
        # Appointment booking
        if query_type == 'appointment' and any(word in query_lower for word in ['book', 'schedule']):
            return self.templates.appointment_booking_nudge()
        
        # Specific medication query
        if query_type == 'medication':
            # Try to extract medication name
            for prescription in patient_context['prescriptions']:
                med_name = prescription['medication'].split()[0].lower()
                if med_name in query_lower:
                    return self.templates.medication_guidance(prescription)
        
        # Side effects
        if 'side effect' in query_lower:
            return self.templates.side_effects_response()
        
        # Worsening symptoms
        if any(word in query_lower for word in ['worse', 'worsening', 'getting worse']):
            return self.templates.symptom_worsening_response()
        
        return None
    
    def _generate_llm_response(
        self,
        query: str,
        patient_context: Dict,
        query_type: str,
        session_id: Optional[str]
    ) -> str:
        """
        Generate response using LLM (HuggingFace Inference API)
        
        Args:
            query: User's query
            patient_context: Patient's medical context
            query_type: Query type
            session_id: Session ID for history
            
        Returns:
            Generated response
        """
        # Choose model based on query type
        model = PRIMARY_MODEL if query_type in ['medication', 'allergy'] else FALLBACK_MODEL
        
        # Build system prompt
        system_prompt = SYSTEM_PROMPT_MEDICAL.format(
            escalation_message=ESCALATION_MESSAGE
        )
        
        # Get conversation history
        history = self._get_history(session_id) if session_id else []
        
        # Build context for the prompt
        patient_info = self.context_retriever.get_formatted_context(patient_context['patient_id'])
        
        # Build conversation context
        conversation_context = ""
        for msg in history[-6:]:  # Last 3 exchanges
            conversation_context += f"User: {msg['query']}\nAssistant: {msg['response']}\n\n"
        
        # Construct the full prompt for HuggingFace
        full_prompt = f"""{system_prompt}

Patient Information:
{patient_info}

{conversation_context}User: {query}
Assistant:"""
        
        # Rate limiting
        self._apply_rate_limit()
        
        # Try with retries
        for attempt in range(MAX_RETRIES + 1):
            try:
                response = self._call_huggingface_api(model, full_prompt)
                if response:
                    return response
                
                # If primary model fails, try fallback model
                if attempt == 0 and model == PRIMARY_MODEL:
                    print(f"⚠️ Primary model failed, trying fallback model...")
                    response = self._call_huggingface_api(FALLBACK_MODEL, full_prompt)
                    if response:
                        return response
                
            except Exception as e:
                print(f"⚠️ Attempt {attempt + 1} failed: {e}")
                if attempt < MAX_RETRIES:
                    time.sleep(2 ** attempt)  # Exponential backoff
        
        # All attempts failed, use fallback
        print("⚠️ All HuggingFace API attempts failed. Using template fallback.")
        return self._generate_fallback_response(query, query_type, patient_context)
    
    def _call_huggingface_api(self, model: str, prompt: str) -> Optional[str]:
        """
        Call HuggingFace Inference API
        
        Args:
            model: Model name/path
            prompt: Full prompt text
            
        Returns:
            Generated text or None if failed
        """
        import os
        token = os.environ.get('HF_API_TOKEN', '') or HF_API_TOKEN
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "temperature": MODEL_TEMPERATURE,
                "max_new_tokens": MAX_TOKENS,
                "return_full_text": False,
                "do_sample": True,
                "top_p": 0.9
            }
        }
        
        try:
            response = requests.post(
                f"{HF_API_BASE_URL}/{model}",
                headers=headers,
                json=payload,
                timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                result = response.json()
                # Handle different response formats
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get('generated_text', '')
                elif isinstance(result, dict):
                    generated_text = result.get('generated_text', '')
                else:
                    generated_text = str(result)
                
                return generated_text.strip()
            
            elif response.status_code == 503:
                # Model is loading
                error_data = response.json()
                estimated_time = error_data.get('estimated_time', 20)
                print(f"⚠️ Model is loading. Estimated time: {estimated_time}s")
                if estimated_time < 30:
                    time.sleep(min(estimated_time + 5, 30))
                    return self._call_huggingface_api(model, prompt)
                return None
            
            elif response.status_code == 429:
                # Rate limit exceeded
                print("⚠️ Rate limit exceeded. Please wait before making more requests.")
                return None
            
            else:
                print(f"⚠️ HuggingFace API error: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return None
        
        except requests.exceptions.Timeout:
            print("⚠️ Request timeout. Model may be overloaded.")
            return None
        except Exception as e:
            print(f"⚠️ Error calling HuggingFace API: {e}")
            return None
    
    def _apply_rate_limit(self):
        """Apply rate limiting between requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < RATE_LIMIT_DELAY:
            time.sleep(RATE_LIMIT_DELAY - time_since_last)
        self.last_request_time = time.time()
    
    def _generate_fallback_response(
        self,
        query: str,
        query_type: str,
        patient_context: Dict
    ) -> str:
        """
        Generate fallback response when LLM is unavailable
        
        Args:
            query: User's query
            query_type: Query type
            patient_context: Patient's medical context
            
        Returns:
            Fallback response
        """
        if query_type == 'medication':
            return self.templates.medication_list(patient_context['prescriptions'])
        elif query_type == 'dietary':
            return self.templates.dietary_advice(
                patient_context['diagnosis'],
                patient_context['allergies']
            )
        elif query_type == 'appointment':
            return self.templates.appointment_booking_nudge()
        elif query_type == 'allergy':
            return self.templates.allergy_information(patient_context['allergies'])
        else:
            return (
                "I can help you with:\n"
                "• Medication information\n"
                "• Dietary advice\n"
                "• Appointment scheduling\n"
                "• Allergy information\n\n"
                "Please ask a specific question about any of these topics!"
            )
    
    def _add_to_history(self, session_id: str, query: str, response: str):
        """Add exchange to conversation history"""
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = []
        
        self.conversation_history[session_id].append({
            'query': query,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        
        # Limit history length
        if len(self.conversation_history[session_id]) > MAX_CONVERSATION_LENGTH:
            self.conversation_history[session_id] = \
                self.conversation_history[session_id][-MAX_CONVERSATION_LENGTH:]
    
    def _get_history(self, session_id: str) -> List[Dict]:
        """Get conversation history for session"""
        return self.conversation_history.get(session_id, [])
    
    def get_conversation_history(self, session_id: str) -> List[Dict]:
        """
        Get conversation history for a session
        
        Args:
            session_id: Session ID
            
        Returns:
            List of conversation exchanges
        """
        return self._get_history(session_id)
    
    def clear_conversation_history(self, session_id: str):
        """
        Clear conversation history for a session
        
        Args:
            session_id: Session ID
        """
        if session_id in self.conversation_history:
            del self.conversation_history[session_id]


# Global instance (singleton pattern)
_chatbot_service = None


def get_chatbot_service() -> ChatbotService:
    """Get or create chatbot service instance"""
    global _chatbot_service
    
    if _chatbot_service is None:
        _chatbot_service = ChatbotService()
    
    return _chatbot_service


# Made with Bob