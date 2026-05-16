"""
Medical Chatbot System with BioMistral Local Inference
Implements patient-grounded Q&A with RAG and safety validation
"""

import torch
import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from sentence_transformers import SentenceTransformer
import faiss
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PatientContext:
    """Structured patient data for grounding responses"""
    patient_id: str
    patient_name: str
    patient_age: int
    diagnosis: str
    appointment_details: str
    symptom: str
    prescription: str
    dietary_restrictions: str
    
    def to_text(self) -> str:
        """Convert patient data to text format for embedding"""
        return f"""
Patient ID: {self.patient_id}
Name: {self.patient_name}
Age: {self.patient_age}
Diagnosis: {self.diagnosis}
Symptoms: {self.symptom}
Prescription: {self.prescription}
Dietary Restrictions: {self.dietary_restrictions}
Appointment Details: {self.appointment_details}
"""


class PatientRAG:
    """Retrieval-Augmented Generation for patient data"""
    
    def __init__(self, embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize RAG system with embedding model
        
        Args:
            embedding_model: HuggingFace model for embeddings
        """
        logger.info(f"Loading embedding model: {embedding_model}")
        self.encoder = SentenceTransformer(embedding_model)
        self.index = None
        self.patient_contexts: List[PatientContext] = []
        self.embeddings = None
        
    def add_patient_data(self, patient_data: Dict):
        """
        Add patient data to the RAG system
        
        Args:
            patient_data: Dictionary containing patient information
        """
        try:
            context = PatientContext(
                patient_id=str(patient_data.get('patient_id', 'N/A')),
                patient_name=patient_data.get('patient_name', 'N/A'),
                patient_age=int(patient_data.get('patient_age', 0)),
                diagnosis=patient_data.get('diagnosis', 'N/A'),
                appointment_details=patient_data.get('appointment_details', 'N/A'),
                symptom=patient_data.get('symptom', 'N/A'),
                prescription=patient_data.get('prescription', 'N/A'),
                dietary_restrictions=patient_data.get('dietary_restrictions', 'N/A')
            )
            self.patient_contexts.append(context)
            logger.info(f"Added patient data for: {context.patient_name}")
        except Exception as e:
            logger.error(f"Error adding patient data: {e}")
            
    def build_index(self):
        """Build FAISS index from patient contexts"""
        if not self.patient_contexts:
            logger.warning("No patient contexts to index")
            return
            
        try:
            # Generate embeddings for all patient contexts
            texts = [ctx.to_text() for ctx in self.patient_contexts]
            self.embeddings = self.encoder.encode(texts, convert_to_numpy=True)
            
            # Build FAISS index
            dimension = self.embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(self.embeddings.astype('float32'))
            
            logger.info(f"Built FAISS index with {len(self.patient_contexts)} patient records")
        except Exception as e:
            logger.error(f"Error building index: {e}")
            
    def retrieve_context(self, query: str, top_k: int = 3) -> List[PatientContext]:
        """
        Retrieve most relevant patient contexts for a query
        
        Args:
            query: User query
            top_k: Number of contexts to retrieve
            
        Returns:
            List of relevant PatientContext objects
        """
        if self.index is None or not self.patient_contexts:
            logger.warning("Index not built or no patient data available")
            return []
            
        try:
            # Encode query
            query_embedding = self.encoder.encode([query], convert_to_numpy=True)
            
            # Search index
            distances, indices = self.index.search(query_embedding.astype('float32'), top_k)
            
            # Return relevant contexts
            relevant_contexts = [self.patient_contexts[idx] for idx in indices[0] if idx < len(self.patient_contexts)]
            logger.info(f"Retrieved {len(relevant_contexts)} relevant contexts for query")
            return relevant_contexts
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return []


class SafetyValidator:
    """Multi-layer safety validation for medical responses"""
    
    # Prohibited patterns that indicate unsafe responses
    UNSAFE_PATTERNS = [
        r'\b(prescribe|prescription)\s+(?!information|details|current)',
        r'\bdiagnos(e|is|ing)\s+(?!information|details|current)',
        r'\b(increase|decrease|stop|start)\s+(medication|medicine|drug)',
        r'\b(self-medicate|self-treat)',
        r'\b(ignore|skip)\s+(doctor|appointment|medical)',
        r'\b(definitely|certainly)\s+(have|are|is)\s+\w+\s+(disease|condition)',
    ]
    
    # Required disclaimers
    REQUIRED_DISCLAIMERS = [
        "consult",
        "healthcare provider",
        "doctor",
        "medical professional"
    ]
    
    @staticmethod
    def validate_response(response: str, patient_context: Optional[PatientContext] = None) -> Tuple[bool, str]:
        """
        Validate response for safety and grounding
        
        Args:
            response: Generated response text
            patient_context: Patient context used for grounding
            
        Returns:
            Tuple of (is_safe, reason)
        """
        response_lower = response.lower()
        
        # Check for unsafe patterns
        for pattern in SafetyValidator.UNSAFE_PATTERNS:
            if re.search(pattern, response_lower):
                return False, f"Response contains unsafe medical advice pattern: {pattern}"
        
        # Check for grounding in patient data
        if patient_context:
            has_patient_reference = any([
                patient_context.patient_name.lower() in response_lower,
                patient_context.diagnosis.lower() in response_lower,
                patient_context.prescription.lower() in response_lower,
                "your record" in response_lower,
                "your file" in response_lower,
                "according to" in response_lower
            ])
            
            if not has_patient_reference and len(response) > 50:
                return False, "Response not grounded in patient data"
        
        # Check for appropriate disclaimers in medical advice
        if any(word in response_lower for word in ['should', 'recommend', 'suggest', 'advise']):
            has_disclaimer = any(disclaimer in response_lower for disclaimer in SafetyValidator.REQUIRED_DISCLAIMERS)
            if not has_disclaimer:
                return False, "Medical advice without appropriate disclaimer"
        
        return True, "Response passed safety validation"
    
    @staticmethod
    def add_safety_disclaimer(response: str) -> str:
        """Add safety disclaimer to response if not present"""
        disclaimer = "\n\nNote: This information is based on your medical records. Always consult your healthcare provider for medical decisions."
        
        if "consult" not in response.lower() and "healthcare provider" not in response.lower():
            return response + disclaimer
        return response


class BioMistralChatbot:
    """BioMistral-based medical chatbot with local inference"""
    
    def __init__(self, model_name: str = "BioMistral/BioMistral-7B", device: str = "auto"):
        """
        Initialize BioMistral chatbot
        
        Args:
            model_name: HuggingFace model identifier
            device: Device for inference ('cuda', 'cpu', or 'auto')
        """
        self.model_name = model_name
        self.device = device
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        self.rag = PatientRAG()
        self.safety_validator = SafetyValidator()
        self.is_loaded = False
        
    def load_model(self):
        """Load BioMistral model and tokenizer"""
        try:
            logger.info(f"Loading BioMistral model: {self.model_name}")
            
            # Determine device
            if self.device == "auto":
                self.device = "cuda" if torch.cuda.is_available() else "cpu"
            
            logger.info(f"Using device: {self.device}")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )
            
            # Load model with optimizations
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map=self.device,
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )
            
            # Create pipeline
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if self.device == "cuda" else -1,
                max_new_tokens=512,
                temperature=0.7,
                top_p=0.9,
                do_sample=True
            )
            
            self.is_loaded = True
            logger.info("BioMistral model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading BioMistral model: {e}")
            logger.info("Falling back to smaller model or CPU inference")
            self._load_fallback_model()
    
    def _load_fallback_model(self):
        """Load a smaller fallback model if BioMistral fails"""
        try:
            fallback_model = "microsoft/BioGPT-Large"
            logger.info(f"Loading fallback model: {fallback_model}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(fallback_model)
            self.model = AutoModelForCausalLM.from_pretrained(
                fallback_model,
                torch_dtype=torch.float32,
                low_cpu_mem_usage=True
            )
            
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=-1,  # CPU
                max_new_tokens=256
            )
            
            self.is_loaded = True
            logger.info("Fallback model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading fallback model: {e}")
            self.is_loaded = False
    
    def initialize_patient_data(self, patient_records: List[Dict]):
        """
        Initialize RAG system with patient data
        
        Args:
            patient_records: List of patient data dictionaries
        """
        logger.info(f"Initializing with {len(patient_records)} patient records")
        
        for record in patient_records:
            self.rag.add_patient_data(record)
        
        self.rag.build_index()
        logger.info("Patient data initialization complete")
    
    def _create_grounded_prompt(self, query: str, contexts: List[PatientContext]) -> str:
        """
        Create a grounded prompt with patient context
        
        Args:
            query: User query
            contexts: Retrieved patient contexts
            
        Returns:
            Formatted prompt string
        """
        if not contexts:
            return f"""You are a medical assistant. Answer the following question based on general medical knowledge, but always recommend consulting a healthcare provider.

Question: {query}

Answer:"""
        
        # Use the most relevant context
        context = contexts[0]
        
        prompt = f"""You are a medical assistant helping with patient inquiries. Answer based ONLY on the patient's medical records provided below. Do not make assumptions or provide information not in the records.

PATIENT MEDICAL RECORD:
{context.to_text()}

IMPORTANT GUIDELINES:
- Only reference information from the patient record above
- If the answer is not in the records, say "I don't have that information in your records"
- Always recommend consulting the healthcare provider for medical decisions
- Do not diagnose, prescribe, or suggest medication changes

PATIENT QUESTION: {query}

ASSISTANT RESPONSE:"""
        
        return prompt
    
    def generate_response(self, query: str, max_retries: int = 2) -> Dict[str, any]:
        """
        Generate a safe, grounded response to user query
        
        Args:
            query: User query
            max_retries: Number of retries if response fails validation
            
        Returns:
            Dictionary with response and metadata
        """
        if not self.is_loaded:
            return {
                "response": "I apologize, but the medical assistant is currently unavailable. Please try again later or contact your healthcare provider directly.",
                "success": False,
                "error": "Model not loaded"
            }
        
        try:
            # Retrieve relevant patient contexts
            contexts = self.rag.retrieve_context(query, top_k=3)
            
            # Create grounded prompt
            prompt = self._create_grounded_prompt(query, contexts)
            
            # Generate response with retries
            for attempt in range(max_retries):
                logger.info(f"Generating response (attempt {attempt + 1}/{max_retries})")
                
                # Generate with pipeline
                outputs = self.pipeline(
                    prompt,
                    max_new_tokens=512,
                    temperature=0.7,
                    top_p=0.9,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
                
                # Extract generated text
                generated_text = outputs[0]['generated_text']
                response = generated_text.split("ASSISTANT RESPONSE:")[-1].strip()
                
                # Validate response
                is_safe, reason = self.safety_validator.validate_response(
                    response,
                    contexts[0] if contexts else None
                )
                
                if is_safe:
                    # Add safety disclaimer
                    response = self.safety_validator.add_safety_disclaimer(response)
                    
                    return {
                        "response": response,
                        "success": True,
                        "grounded": len(contexts) > 0,
                        "patient_context": contexts[0].patient_name if contexts else None
                    }
                else:
                    logger.warning(f"Response failed validation: {reason}")
            
            # If all retries failed, return safe fallback
            return {
                "response": "I apologize, but I cannot provide a safe response to that query. Please consult your healthcare provider directly for medical advice.",
                "success": False,
                "error": "Response validation failed after retries"
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                "response": "I apologize, but I encountered an error processing your request. Please try again or contact your healthcare provider.",
                "success": False,
                "error": str(e)
            }
    
    def chat(self, query: str) -> str:
        """
        Simple chat interface
        
        Args:
            query: User query
            
        Returns:
            Response string
        """
        result = self.generate_response(query)
        return result.get("response", "I apologize, but I cannot process your request at this time.")


# Utility functions for prompt engineering
def create_medical_context_prompt(patient_data: Dict, query: str) -> str:
    """
    Create a medical context-aware prompt
    
    Args:
        patient_data: Patient information dictionary
        query: User query
        
    Returns:
        Formatted prompt
    """
    return f"""Based on the following patient information, answer the question accurately and safely.

Patient Information:
- Name: {patient_data.get('patient_name', 'N/A')}
- Age: {patient_data.get('patient_age', 'N/A')}
- Diagnosis: {patient_data.get('diagnosis', 'N/A')}
- Current Symptoms: {patient_data.get('symptom', 'N/A')}
- Prescription: {patient_data.get('prescription', 'N/A')}
- Dietary Restrictions: {patient_data.get('dietary_restrictions', 'N/A')}

Question: {query}

Provide a helpful response based on the patient's records. Always recommend consulting their healthcare provider for medical decisions.

Response:"""


def extract_medical_entities(text: str) -> Dict[str, List[str]]:
    """
    Extract medical entities from text (simple regex-based)
    
    Args:
        text: Input text
        
    Returns:
        Dictionary of entity types and values
    """
    entities = {
        "medications": [],
        "symptoms": [],
        "conditions": []
    }
    
    # Simple pattern matching (can be enhanced with NER models)
    medication_patterns = r'\b(tablet|capsule|mg|ml|medication|medicine|drug)\b'
    symptom_patterns = r'\b(pain|fever|cough|nausea|headache|fatigue)\b'
    
    if re.search(medication_patterns, text.lower()):
        entities["medications"] = re.findall(r'\b\w+\s+(?:tablet|capsule|mg)\b', text.lower())
    
    if re.search(symptom_patterns, text.lower()):
        entities["symptoms"] = re.findall(symptom_patterns, text.lower())
    
    return entities

# Made with Bob
