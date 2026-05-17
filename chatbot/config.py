"""
Chatbot Configuration (FIXED FOR HF INFERENCE STABILITY)
"""

import os
from dotenv import load_dotenv

load_dotenv()

# HuggingFace
HF_API_TOKEN = os.getenv("HF_API_TOKEN", "").strip()
HF_API_BASE_URL = "https://api-inference.huggingface.co/models"

# ✅ Stable inference-safe models
# BioMistral - Medical domain specialized model
PRIMARY_MODEL = "BioMistral/BioMistral-7B"
# Alternative medical models
FALLBACK_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"

# Model Parameters
MODEL_TEMPERATURE = 0.3
MAX_TOKENS = 500
REQUEST_TIMEOUT = 40
MAX_RETRIES = 2

# Rate Limiting
RATE_LIMIT_DELAY = 1.0

# Safety thresholds
CONFIDENCE_THRESHOLD = 0.70
ESCALATION_THRESHOLD = 0.50
MAX_CONVERSATION_LENGTH = 20

# Unsafe patterns
UNSAFE_PATTERNS = [
    r'\b(stop|quit|discontinue)\s+(taking|medication|drug)',
    r'\b(diagnose|what\s+do\s+i\s+have|what\'s\s+wrong)',
    r'\b(change|modify|adjust)\s+(dose|dosage|medication)',
    r'\b(replace|substitute)\s+(medication|drug)',
    r'\b(emergency|chest\s+pain|difficulty\s+breathing)',
]

ESCALATION_KEYWORDS = [
    "emergency", "chest pain", "difficulty breathing",
    "unconscious", "stroke", "seizure", "overdose"
]

# Messages
ESCALATION_MESSAGE = (
    "I'm unable to confidently answer this. Please consult a healthcare professional."
)

EMERGENCY_MESSAGE = (
    "⚠️ Medical emergency detected. Please contact emergency services immediately."
)

UNSAFE_REQUEST_MESSAGE = (
    "I cannot assist with medical treatment decisions. Please consult your doctor regarding: {topic}"
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