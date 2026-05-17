"""
Chatbot Configuration
Settings for LLM, safety thresholds, and behavior
"""

import os

# HuggingFace Configuration
HF_API_TOKEN = os.environ.get('HF_API_TOKEN', '')  # Set via environment variable
HF_API_BASE_URL = "https://api-inference.huggingface.co/models"

# Medical Models on HuggingFace
# BioMistral - Medical domain specialized model
PRIMARY_MODEL = "BioMistral/BioMistral-7B"
# Alternative medical models
FALLBACK_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"
# Other options: "epfl-llm/meditron-7b", "microsoft/BioGPT-Large"

# Model Parameters
MODEL_TEMPERATURE = 0.3          # Lower = more conservative/factual
MAX_TOKENS = 500                 # Maximum response length
REQUEST_TIMEOUT = 30             # API request timeout in seconds
MAX_RETRIES = 2                  # Number of retries on API failure

# Rate Limiting
RATE_LIMIT_DELAY = 1.0          # Delay between requests in seconds

# Safety Thresholds
CONFIDENCE_THRESHOLD = 0.70      # Minimum confidence to provide answer
ESCALATION_THRESHOLD = 0.50      # Below this, escalate to doctor
MAX_CONVERSATION_LENGTH = 20     # Maximum messages in history

# Unsafe Query Patterns (regex patterns to detect)
UNSAFE_PATTERNS = [
    r'\b(stop|quit|discontinue|cease)\s+(taking|medication|medicine|drug|prescription)',
    r'\b(diagnose|diagnosis|what\s+do\s+i\s+have|what\'s\s+wrong\s+with\s+me)',
    r'\b(change|modify|adjust|increase|decrease)\s+(dose|dosage|medication|prescription)',
    r'\b(instead\s+of|replace|substitute)\s+(medication|medicine|drug)',
    r'\b(emergency|urgent|severe\s+pain|chest\s+pain|difficulty\s+breathing)',
]

# Escalation Triggers
ESCALATION_KEYWORDS = [
    'emergency', 'urgent', 'severe', 'chest pain', 'difficulty breathing',
    'unconscious', 'bleeding heavily', 'allergic reaction', 'overdose',
    'suicidal', 'heart attack', 'stroke', 'seizure'
]

# Response Templates
ESCALATION_MESSAGE = (
    "I'm unable to confidently answer this based on your medical records. "
    "Please consult your doctor for medical advice."
)

EMERGENCY_MESSAGE = (
    "⚠️ This sounds like a medical emergency. Please call emergency services "
    "immediately or go to the nearest emergency room. If you're experiencing "
    "severe symptoms, do not wait."
)

UNSAFE_REQUEST_MESSAGE = (
    "I cannot provide guidance on this matter as it involves medical decisions "
    "that require professional consultation. Please speak with your doctor about: {topic}"
)

# Dietary Advice by Diagnosis
DIETARY_GUIDELINES = {
    'upper respiratory tract infection': {
        'recommended': [
            'Warm fluids (herbal tea, warm water with honey)',
            'Chicken soup or broth',
            'Soft, easy-to-swallow foods',
            'Fruits rich in Vitamin C (oranges, kiwi)',
            'Ginger tea for throat relief'
        ],
        'avoid': [
            'Dairy products (may increase mucus)',
            'Cold beverages',
            'Spicy or acidic foods',
            'Alcohol and caffeine'
        ]
    },
    'allergic rhinitis': {
        'recommended': [
            'Anti-inflammatory foods (turmeric, ginger)',
            'Omega-3 rich foods (salmon, walnuts)',
            'Quercetin-rich foods (apples, onions)',
            'Probiotic foods (yogurt, kefir)',
            'Green tea'
        ],
        'avoid': [
            'Histamine-rich foods (aged cheese, wine)',
            'Processed foods',
            'Foods you\'re allergic to',
            'Excessive sugar'
        ]
    },
    'hypertension': {
        'recommended': [
            'DASH diet foods (fruits, vegetables)',
            'Whole grains',
            'Low-fat dairy',
            'Lean proteins (fish, poultry)',
            'Potassium-rich foods (bananas, spinach)',
            'Foods with magnesium (nuts, seeds)'
        ],
        'avoid': [
            'High sodium foods',
            'Processed and canned foods',
            'Excessive alcohol',
            'Saturated fats',
            'Caffeine (limit intake)'
        ]
    },
    'default': {
        'recommended': [
            'Balanced diet with fruits and vegetables',
            'Adequate hydration (8 glasses of water daily)',
            'Whole grains and lean proteins',
            'Regular meal times'
        ],
        'avoid': [
            'Excessive processed foods',
            'High sugar intake',
            'Excessive alcohol',
            'Foods you\'re allergic to'
        ]
    }
}

# Medication Timing Guidelines
MEDICATION_TIMING = {
    'with food': 'Take this medication with a meal or snack to reduce stomach upset.',
    'before food': 'Take this medication 30-60 minutes before eating for best absorption.',
    'after food': 'Take this medication after eating to minimize side effects.',
    'with breakfast': 'Take this medication with your morning meal.',
    'in the evening': 'Take this medication in the evening, preferably at the same time each day.',
    'at bedtime': 'Take this medication before going to bed.',
    'twice daily': 'Take this medication approximately 12 hours apart (e.g., 8 AM and 8 PM).',
    'once daily': 'Take this medication at the same time each day for consistency.'
}

# System Prompts
SYSTEM_PROMPT_MEDICAL = """You are a helpful medical assistant chatbot for post-consultation patient support. 

Your role is to:
- Answer questions about the patient's existing prescriptions and medications
- Provide medication guidance based on their current prescriptions
- Offer diagnosis-aware dietary advice
- Answer general post-consultation questions
- Direct patients to schedule appointments when needed

You MUST NOT:
- Diagnose new conditions or diseases
- Modify, change, or recommend stopping prescribed medications
- Provide medical advice outside the patient's existing treatment plan
- Invent or hallucinate medical information
- Give advice on emergency situations (escalate immediately)

If you are uncertain or the question is outside your scope, respond with:
"{escalation_message}"

Always base your responses on the patient's medical context provided. Be empathetic, clear, and concise.
"""

SYSTEM_PROMPT_GENERAL = """You are a helpful assistant providing general health and lifestyle guidance.

You can help with:
- General dietary advice and nutrition
- Lifestyle recommendations
- General health questions
- Appointment scheduling guidance

You MUST NOT:
- Diagnose medical conditions
- Recommend specific medications
- Provide emergency medical advice
- Replace professional medical consultation

Be helpful, empathetic, and always encourage consulting healthcare professionals for medical concerns.
"""

# Made with Bob