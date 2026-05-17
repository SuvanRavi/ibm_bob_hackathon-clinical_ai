"""
AI Medical Chatbot Module
Provides safe, context-aware medical assistance for patients
"""

from .service import ChatbotService
from .context import PatientContextRetriever
from .safety import SafetyValidator
from .templates import ResponseTemplates

__all__ = [
    'ChatbotService',
    'PatientContextRetriever',
    'SafetyValidator',
    'ResponseTemplates'
]

__version__ = '1.0.0'

# Made with Bob
