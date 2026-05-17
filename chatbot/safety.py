"""
Safety Validator
Validates queries and responses to prevent unsafe medical advice
"""

import re
from typing import Dict, List, Tuple, Optional
from .config import (
    UNSAFE_PATTERNS,
    ESCALATION_KEYWORDS,
    ESCALATION_MESSAGE,
    EMERGENCY_MESSAGE,
    UNSAFE_REQUEST_MESSAGE,
    CONFIDENCE_THRESHOLD,
    ESCALATION_THRESHOLD
)


class SafetyValidator:
    """Validates chatbot queries and responses for safety"""
    
    def __init__(self):
        """Initialize safety validator"""
        self.unsafe_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in UNSAFE_PATTERNS]
        self.escalation_keywords = [kw.lower() for kw in ESCALATION_KEYWORDS]
    
    def validate_query(self, query: str) -> Tuple[bool, Optional[str]]:
        """
        Validate user query for safety
        
        Args:
            query: User's question/query
            
        Returns:
            Tuple of (is_safe, error_message)
            - is_safe: True if query is safe to process
            - error_message: Error message if unsafe, None if safe
        """
        query_lower = query.lower()
        
        # Check for emergency keywords
        if self._is_emergency(query_lower):
            return False, EMERGENCY_MESSAGE
        
        # Check for unsafe patterns
        unsafe_match = self._check_unsafe_patterns(query)
        if unsafe_match:
            topic = unsafe_match.group(0)
            return False, UNSAFE_REQUEST_MESSAGE.format(topic=topic)
        
        # Check for diagnosis requests
        if self._is_diagnosis_request(query_lower):
            return False, UNSAFE_REQUEST_MESSAGE.format(
                topic="diagnosing new conditions or symptoms"
            )
        
        # Check for prescription modification requests
        if self._is_prescription_modification(query_lower):
            return False, UNSAFE_REQUEST_MESSAGE.format(
                topic="changing or modifying your prescriptions"
            )
        
        return True, None
    
    def _is_emergency(self, query: str) -> bool:
        """Check if query indicates an emergency"""
        return any(keyword in query for keyword in self.escalation_keywords)
    
    def _check_unsafe_patterns(self, query: str) -> Optional[re.Match]:
        """Check if query matches unsafe patterns"""
        for pattern in self.unsafe_patterns:
            match = pattern.search(query)
            if match:
                return match
        return None
    
    def _is_diagnosis_request(self, query: str) -> bool:
        """Check if query is requesting a new diagnosis"""
        diagnosis_indicators = [
            'what do i have',
            'what\'s wrong with me',
            'do i have',
            'am i sick',
            'diagnose me',
            'what disease',
            'what condition',
            'is this cancer',
            'is this serious'
        ]
        return any(indicator in query for indicator in diagnosis_indicators)
    
    def _is_prescription_modification(self, query: str) -> bool:
        """Check if query is requesting prescription changes"""
        modification_indicators = [
            'change my medication',
            'change my prescription',
            'switch medication',
            'different medication',
            'stop taking',
            'quit taking',
            'discontinue',
            'increase dose',
            'decrease dose',
            'take more',
            'take less'
        ]
        return any(indicator in query for indicator in modification_indicators)
    
    def validate_response(
        self,
        response: str,
        patient_context: Dict,
        confidence: float = 1.0
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate chatbot response for safety
        
        Args:
            response: Generated response
            patient_context: Patient's medical context
            confidence: Confidence score of the response (0-1)
            
        Returns:
            Tuple of (is_safe, modified_response)
            - is_safe: True if response is safe
            - modified_response: Modified response if needed, None if original is safe
        """
        # Check confidence threshold
        if confidence < ESCALATION_THRESHOLD:
            return False, ESCALATION_MESSAGE
        
        # Check if response contains hallucinated medications
        if self._contains_hallucinated_medications(response, patient_context):
            return False, ESCALATION_MESSAGE
        
        # Check if response recommends stopping medications
        if self._recommends_stopping_medication(response):
            return False, UNSAFE_REQUEST_MESSAGE.format(
                topic="stopping or changing medications"
            )
        
        # Check if response makes new diagnoses
        if self._makes_new_diagnosis(response, patient_context):
            return False, ESCALATION_MESSAGE
        
        # Warn if confidence is moderate
        if confidence < CONFIDENCE_THRESHOLD:
            warning = (
                "\n\n⚠️ Note: I have moderate confidence in this answer. "
                "Please verify with your healthcare provider if you have concerns."
            )
            return True, response + warning
        
        return True, None
    
    def _contains_hallucinated_medications(
        self,
        response: str,
        patient_context: Dict
    ) -> bool:
        """Check if response mentions medications not in patient's prescriptions"""
        # Get patient's actual medications
        actual_meds = set()
        for prescription in patient_context.get('prescriptions', []):
            med_name = prescription['medication'].lower()
            # Extract base medication name (before dosage)
            base_name = med_name.split()[0]
            actual_meds.add(base_name)
        
        # Common medication keywords that might appear in response
        medication_keywords = [
            'take', 'medication', 'medicine', 'drug', 'prescription',
            'pill', 'tablet', 'capsule', 'dose', 'dosage'
        ]
        
        # If response mentions medications, check if they're in patient's list
        response_lower = response.lower()
        if any(keyword in response_lower for keyword in medication_keywords):
            # Extract potential medication names (simplified check)
            # This is a basic check - in production, use NER or drug database
            words = response_lower.split()
            for i, word in enumerate(words):
                # Check for medication-like patterns
                if word.endswith('cillin') or word.endswith('mycin') or word.endswith('pril'):
                    # Check if this medication is in patient's list
                    if word not in actual_meds and not any(word in med for med in actual_meds):
                        # Potential hallucination detected
                        return True
        
        return False
    
    def _recommends_stopping_medication(self, response: str) -> bool:
        """Check if response recommends stopping medication"""
        stop_indicators = [
            'stop taking',
            'discontinue',
            'quit taking',
            'cease taking',
            'don\'t take',
            'avoid taking',
            'skip your medication'
        ]
        response_lower = response.lower()
        return any(indicator in response_lower for indicator in stop_indicators)
    
    def _makes_new_diagnosis(self, response: str, patient_context: Dict) -> bool:
        """Check if response makes a diagnosis not in patient's records"""
        current_diagnosis = patient_context.get('diagnosis', '').lower()
        
        diagnosis_phrases = [
            'you have',
            'you are diagnosed with',
            'this is',
            'this indicates',
            'you suffer from',
            'you\'re experiencing'
        ]
        
        response_lower = response.lower()
        
        # Check if response makes diagnostic statements
        for phrase in diagnosis_phrases:
            if phrase in response_lower:
                # Check if it's about the existing diagnosis
                if current_diagnosis not in response_lower:
                    # Might be making a new diagnosis
                    return True
        
        return False
    
    def should_escalate(self, query: str, confidence: float) -> bool:
        """
        Determine if query should be escalated to a doctor
        
        Args:
            query: User's query
            confidence: Confidence score
            
        Returns:
            True if should escalate, False otherwise
        """
        # Escalate if confidence is too low
        if confidence < ESCALATION_THRESHOLD:
            return True
        
        # Escalate if emergency
        if self._is_emergency(query.lower()):
            return True
        
        # Escalate if complex medical question
        complex_indicators = [
            'side effect',
            'interaction',
            'reaction',
            'complication',
            'worsening',
            'not working',
            'still sick'
        ]
        
        query_lower = query.lower()
        if any(indicator in query_lower for indicator in complex_indicators):
            return True
        
        return False
    
    def get_escalation_response(self, reason: str = "general") -> str:
        """
        Get appropriate escalation response
        
        Args:
            reason: Reason for escalation
            
        Returns:
            Escalation message
        """
        if reason == "emergency":
            return EMERGENCY_MESSAGE
        elif reason == "unsafe":
            return UNSAFE_REQUEST_MESSAGE.format(topic="this matter")
        else:
            return ESCALATION_MESSAGE
    
    def sanitize_response(self, response: str) -> str:
        """
        Sanitize response to remove potentially unsafe content
        
        Args:
            response: Original response
            
        Returns:
            Sanitized response
        """
        # Remove any diagnostic language
        unsafe_phrases = [
            'you definitely have',
            'you certainly have',
            'this is definitely',
            'you need to stop',
            'don\'t take your medication'
        ]
        
        sanitized = response
        for phrase in unsafe_phrases:
            sanitized = sanitized.replace(phrase, '[removed for safety]')
        
        return sanitized


# Global instance (singleton pattern)
_safety_validator = None


def get_safety_validator() -> SafetyValidator:
    """Get or create safety validator instance"""
    global _safety_validator
    
    if _safety_validator is None:
        _safety_validator = SafetyValidator()
    
    return _safety_validator


# Made with Bob