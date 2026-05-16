from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import requests
import json
import os

app = Flask(__name__)

# Hugging Face API Configuration
HF_API_TOKEN = os.environ.get('OPENAI_API_KEY')  # Replace with your actual token
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"

# Mock data for available time slots
available_slots = {
    '2026-05-17': ['09:00 AM', '10:00 AM', '11:00 AM', '02:00 PM', '03:00 PM', '04:00 PM'],
    '2026-05-18': ['09:00 AM', '10:00 AM', '11:00 AM', '02:00 PM', '03:00 PM'],
    '2026-05-19': ['09:00 AM', '11:00 AM', '02:00 PM', '03:00 PM', '04:00 PM'],
    '2026-05-20': ['10:00 AM', '11:00 AM', '02:00 PM', '03:00 PM', '04:00 PM'],
    '2026-05-21': ['09:00 AM', '10:00 AM', '02:00 PM', '03:00 PM'],
}

# Mock data for booked appointments
booked_appointments = []

# Mock data for medication reminders
medication_reminders = [
    {
        'medication': 'Amoxicillin 500mg',
        'time': '08:00 AM',
        'frequency': 'Twice daily',
        'notes': 'Take with food'
    },
    {
        'medication': 'Vitamin D3',
        'time': '09:00 AM',
        'frequency': 'Once daily',
        'notes': 'Take with breakfast'
    },
    {
        'medication': 'Blood Pressure Check',
        'time': '07:00 PM',
        'frequency': 'Daily',
        'notes': 'Record readings in log'
    }
]

# Mock data for upcoming tasks
upcoming_tasks = [
    {
        'task': 'Lab Test - Blood Work',
        'date': '2026-05-18',
        'time': '08:30 AM',
        'location': 'City Medical Lab, 2nd Floor'
    },
    {
        'task': 'Physical Therapy Session',
        'date': '2026-05-20',
        'time': '03:00 PM',
        'location': 'Rehabilitation Center, Room 204'
    }
]

# Mock data for patient profile
patient_profile = {
    'name': 'John Anderson',
    'age': 45,
    'blood_group': 'O+',
    'contact_number': '+1 (555) 123-4567',
    'email': 'john.anderson@email.com',
    'primary_doctor': {
        'name': 'Dr. Sarah Johnson',
        'specialty': 'General Practitioner',
        'contact': '+1 (555) 234-5678'
    },
    'allergies': ['Penicillin', 'Peanuts', 'Latex'],
    'current_medications': [
        'Amoxicillin 500mg - Twice daily',
        'Vitamin D3 - Once daily',
        'Lisinopril 10mg - Once daily'
    ],
    'emergency_contact': {
        'name': 'Sarah Anderson',
        'phone': '+1 (555) 987-6543',
        'relationship': 'Spouse'
    },
    'current_health_status': {
        'active_diagnoses': [
            {
                'condition': 'Acute Pharyngitis',
                'status': 'Under Treatment',
                'diagnosed_date': '2026-05-15'
            }
        ],
        'active_symptoms': [
            'Sore throat',
            'Low grade fever',
            'Fatigue',
            'Difficulty swallowing'
        ]
    }
}

# Medical Knowledge Base for AI Assistant
MEDICAL_KNOWLEDGE_BASE = {
    'medications': {
        'amoxicillin': {
            'name': 'Amoxicillin 500mg',
            'purpose': 'Amoxicillin is an antibiotic used to treat bacterial infections, including throat infections like your Acute Pharyngitis.',
            'dosage': 'Take 500mg twice daily as prescribed by Dr. Sarah Johnson.',
            'side_effects': 'Common side effects may include nausea, diarrhea, or rash. Contact your doctor if symptoms worsen.',
            'precautions': 'Take with food to reduce stomach upset. Complete the full course even if you feel better.',
            'interactions': 'Avoid alcohol while taking Amoxicillin as it may reduce effectiveness and increase side effects.'
        },
        'paracetamol': {
            'name': 'Paracetamol (Acetaminophen)',
            'purpose': 'Used to reduce fever and relieve pain, including sore throat pain.',
            'dosage': 'Take 500-1000mg every 4-6 hours as needed, not exceeding 4000mg per day.',
            'side_effects': 'Generally well-tolerated. Rare side effects include allergic reactions.',
            'precautions': 'Do not exceed recommended dose. Avoid alcohol to prevent liver damage.',
            'interactions': 'Safe with most medications, but inform your doctor of all medicines you take.'
        },
        'vitamin d3': {
            'name': 'Vitamin D3',
            'purpose': 'Supports immune system function and bone health.',
            'dosage': 'Take once daily with breakfast as prescribed.',
            'side_effects': 'Rare when taken as directed.',
            'precautions': 'Take with food for better absorption.',
            'interactions': 'Generally safe with other medications.'
        },
        'lisinopril': {
            'name': 'Lisinopril 10mg',
            'purpose': 'Used to treat high blood pressure.',
            'dosage': 'Take 10mg once daily as prescribed.',
            'side_effects': 'May cause dizziness, dry cough, or fatigue.',
            'precautions': 'Rise slowly from sitting/lying position to prevent dizziness.',
            'interactions': 'Avoid potassium supplements unless directed by your doctor.'
        }
    },
    'conditions': {
        'acute pharyngitis': {
            'name': 'Acute Pharyngitis',
            'description': 'Inflammation of the throat (pharynx), commonly known as a sore throat, often caused by bacterial infection.',
            'symptoms': 'Sore throat, difficulty swallowing, fever, swollen lymph nodes.',
            'treatment': 'Antibiotics (Amoxicillin), rest, hydration, and pain relievers.',
            'dietary_advice': [
                'Drink plenty of warm fluids (warm water, herbal tea, warm soup)',
                'Avoid spicy, acidic, or rough foods that may irritate your throat',
                'Eat soft, easy-to-swallow foods like yogurt, mashed potatoes, or smoothies',
                'Stay hydrated - aim for 8-10 glasses of water daily',
                'Avoid alcohol while on antibiotics',
                'Honey and lemon in warm water can soothe throat pain'
            ],
            'recovery_time': 'Most patients recover within 7-10 days with proper treatment.',
            'warning_signs': 'Seek immediate care if you experience difficulty breathing, severe pain, or high fever above 103°F.'
        }
    }
}

# Safety keywords that trigger escalation
SAFETY_KEYWORDS = {
    'emergency': ['emergency', 'urgent', 'severe pain', 'chest pain', 'difficulty breathing',
                  'can\'t breathe', 'heart attack', 'stroke', 'bleeding heavily', 'unconscious'],
    'diagnosis': ['diagnose', 'do i have', 'is this', 'could this be', 'what disease'],
    'dosage_change': ['change dose', 'increase dose', 'decrease dose', 'stop taking',
                      'can i take more', 'double dose', 'skip dose'],
    'substitute': ['substitute', 'replace medicine', 'alternative medicine', 'switch to',
                   'instead of', 'can i take instead']
}

# Dangerous keywords to check in AI responses
DANGEROUS_RESPONSE_KEYWORDS = [
    'stop taking medication',
    'stop your medication',
    'discontinue medication',
    'increase your dose',
    'decrease your dose',
    'change your dose',
    'you should stop',
    'emergency room',
    'call 911',
    'seek immediate',
    'go to hospital'
]

def query_ai_model(payload):
    """
    Query the Hugging Face BioMistral-7B model
    Returns the AI-generated text or an error message
    """
    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        
        # Handle model loading time
        if response.status_code == 503:
            error_data = response.json()
            if 'estimated_time' in error_data:
                return {
                    'error': True,
                    'message': f"Model is loading. Please wait approximately {error_data['estimated_time']:.0f} seconds and try again."
                }
            return {
                'error': True,
                'message': "Model is currently loading. Please try again in a moment."
            }
        
        # Handle rate limiting
        if response.status_code == 429:
            return {
                'error': True,
                'message': "Rate limit exceeded. Please wait a moment before trying again."
            }
        
        # Handle authentication errors
        if response.status_code == 401:
            return {
                'error': True,
                'message': "API authentication failed. Please check the API token configuration."
            }
        
        # Handle successful response
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return {
                    'error': False,
                    'text': result[0].get('generated_text', '')
                }
            return {
                'error': True,
                'message': "Unexpected response format from AI model."
            }
        
        # Handle other errors
        return {
            'error': True,
            'message': f"API request failed with status code {response.status_code}"
        }
        
    except requests.exceptions.Timeout:
        return {
            'error': True,
            'message': "Request timed out. The AI model may be busy. Please try again."
        }
    except requests.exceptions.RequestException as e:
        return {
            'error': True,
            'message': f"Network error: {str(e)}"
        }
    except Exception as e:
        return {
            'error': True,
            'message': f"Unexpected error: {str(e)}"
        }

def check_response_safety(ai_response):
    """
    Check if AI response contains dangerous keywords
    Returns (is_safe, warning_message)
    """
    response_lower = ai_response.lower()
    
    for keyword in DANGEROUS_RESPONSE_KEYWORDS:
        if keyword in response_lower:
            return False, "⚠️ **Safety Override**: This response has been flagged for containing potentially dangerous medical advice. Please consult your doctor directly for any changes to your treatment plan."
    
    return True, None

def get_ai_response(user_message, patient_context):
    """
    Generate AI response with safety guardrails
    """
    message_lower = user_message.lower()
    
    # Safety Check 1: Emergency keywords
    for keyword in SAFETY_KEYWORDS['emergency']:
        if keyword in message_lower:
            return {
                'response': '🚨 **EMERGENCY ALERT**: If you are experiencing a medical emergency, please call 911 immediately or go to the nearest emergency room. Do not wait for a response here.',
                'type': 'emergency',
                'escalate': True
            }
    
    # Safety Check 2: Diagnosis requests
    for keyword in SAFETY_KEYWORDS['diagnosis']:
        if keyword in message_lower:
            doctor_name = patient_context.get('primary_doctor', {}).get('name', 'your doctor')
            current_diagnosis = patient_context['current_health_status']['active_diagnoses'][0]['condition']
            return {
                'response': f'⚠️ **Safety Notice**: I cannot provide medical diagnoses. Your current diagnosis of {current_diagnosis} was made by {doctor_name}. If you have concerns about new symptoms or your condition, please contact {doctor_name} directly at the clinic.',
                'type': 'safety_warning',
                'escalate': True
            }
    
    # Safety Check 3: Dosage changes
    for keyword in SAFETY_KEYWORDS['dosage_change']:
        if keyword in message_lower:
            doctor_name = patient_context.get('primary_doctor', {}).get('name', 'your doctor')
            return {
                'response': f'⚠️ **Safety Notice**: For your safety, I cannot advise on changing medication dosages. Your current prescriptions were carefully determined by {doctor_name}. Please contact {doctor_name} before making any changes to your medication regimen.',
                'type': 'safety_warning',
                'escalate': True
            }
    
    # Safety Check 4: Medicine substitution
    for keyword in SAFETY_KEYWORDS['substitute']:
        if keyword in message_lower:
            doctor_name = patient_context.get('primary_doctor', {}).get('name', 'your doctor')
            allergies = ', '.join(patient_context.get('allergies', []))
            allergy_note = f', especially considering your allergies to {allergies}' if allergies else ''
            return {
                'response': f'⚠️ **Safety Notice**: I cannot recommend substituting or changing your prescribed medications. Please consult {doctor_name} before making any medication changes{allergy_note}.',
                'type': 'safety_warning',
                'escalate': True
            }
    
    # Feature 3: Dietary Advice
    if any(word in message_lower for word in ['diet', 'food', 'eat', 'drink', 'nutrition', 'meal']):
        condition = patient_context['current_health_status']['active_diagnoses'][0]['condition'].lower()
        doctor_name = patient_context.get('primary_doctor', {}).get('name', 'your doctor')
        if condition in MEDICAL_KNOWLEDGE_BASE['conditions']:
            dietary_advice = MEDICAL_KNOWLEDGE_BASE['conditions'][condition]['dietary_advice']
            advice_text = '\n'.join([f"• {advice}" for advice in dietary_advice])
            return {
                'response': f'**Dietary Recommendations for {patient_context["current_health_status"]["active_diagnoses"][0]["condition"]}:**\n\n{advice_text}\n\nThese recommendations are based on your current diagnosis and medications. Always follow {doctor_name}\'s specific dietary instructions.',
                'type': 'dietary_advice',
                'escalate': False
            }
    
    # Feature 2: Medication Q&A
    if any(word in message_lower for word in ['medicine', 'medication', 'drug', 'pill', 'amoxicillin', 'paracetamol', 'vitamin', 'lisinopril']):
        doctor_name = patient_context.get('primary_doctor', {}).get('name', 'your doctor')
        medications = patient_context.get('current_medications', [])
        
        # Check for missed dose question
        if 'missed' in message_lower or 'forgot' in message_lower:
            primary_med = medications[0] if medications else 'your medication'
            return {
                'response': f'**Missed Dose Information:**\n\nIf you missed a dose of {primary_med}:\n• Take it as soon as you remember\n• If it\'s almost time for your next dose, skip the missed dose\n• Do NOT double up on doses\n• Continue with your regular schedule\n\nFor other medications, please contact {doctor_name} for specific guidance.',
                'type': 'medication_info',
                'escalate': False
            }
        
        # General medication information
        for med_key, med_info in MEDICAL_KNOWLEDGE_BASE['medications'].items():
            if med_key in message_lower:
                return {
                    'response': f'**{med_info["name"]}**\n\n**Purpose:** {med_info["purpose"]}\n\n**Dosage:** {med_info["dosage"]}\n\n**Precautions:** {med_info["precautions"]}\n\n**Important:** {med_info["interactions"]}',
                    'type': 'medication_info',
                    'escalate': False
                }
        
        # General medication response
        med_list = ', '.join([med.split(' - ')[0] for med in medications]) if medications else 'your medications'
        return {
            'response': f'I can provide information about your current medications: {med_list}. Which medication would you like to know more about?',
            'type': 'medication_info',
            'escalate': False
        }
    
    # Symptom inquiry
    if any(word in message_lower for word in ['symptom', 'sore throat', 'fever', 'pain', 'swallow', 'throat']):
        doctor_name = patient_context.get('primary_doctor', {}).get('name', 'your doctor')
        diagnosis = patient_context['current_health_status']['active_diagnoses'][0]['condition']
        symptoms = patient_context['current_health_status']['active_symptoms']
        return {
            'response': f'**Your Current Symptoms:**\n\nBased on your diagnosis of {diagnosis}, you are experiencing:\n• {", ".join(symptoms)}\n\nThese symptoms should improve within 7-10 days with your current treatment. If symptoms worsen or you develop new concerning symptoms, please contact {doctor_name}.',
            'type': 'symptom_info',
            'escalate': False
        }
    
    # Default helpful response
    doctor_name = patient_context.get('primary_doctor', {}).get('name', 'your doctor')
    medications = patient_context.get('current_medications', [])
    diagnosis = patient_context['current_health_status']['active_diagnoses'][0]['condition']
    med_list = ', '.join([med.split(' - ')[0] for med in medications]) if medications else 'your medications'
    
    return {
        'response': f'I\'m here to help answer questions about:\n\n• Your medications ({med_list})\n• Dietary recommendations for {diagnosis}\n• Your current symptoms and treatment\n• General post-consultation care\n\nWhat would you like to know more about?\n\n*For medical emergencies, call 911. For changes to your treatment plan, contact {doctor_name}.*',
        'type': 'general',
        'escalate': False
    }

@app.route('/')
def index():
    return render_template('schedule.html', 
                         available_slots=available_slots,
                         booked_appointments=booked_appointments,
                         medication_reminders=medication_reminders,
                         upcoming_tasks=upcoming_tasks)

@app.route('/schedule')
def schedule():
    return render_template('schedule.html',
                         available_slots=available_slots,
                         booked_appointments=booked_appointments,
                         medication_reminders=medication_reminders,
                         upcoming_tasks=upcoming_tasks)

@app.route('/appointments')
def appointments():
    return render_template('appointments.html',
                         booked_appointments=booked_appointments)

@app.route('/profile')
def profile():
    return render_template('profile.html',
                         patient_profile=patient_profile)

@app.route('/assistant')
def assistant():
    return render_template('assistant.html',
                         patient_profile=patient_profile,
                         medication_reminders=medication_reminders)

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({
                'success': False,
                'message': 'Message cannot be empty'
            }), 400
        
        # First, check safety guardrails (emergency, diagnosis, dosage changes)
        ai_response = get_ai_response(user_message, patient_profile)
        
        # If safety check triggered, return immediately without calling AI
        if ai_response['escalate']:
            return jsonify({
                'success': True,
                'response': ai_response['response'],
                'type': ai_response['type'],
                'escalate': ai_response['escalate']
            })
        
        # If safety checks passed, construct prompt for AI model
        diagnosis = patient_profile['current_health_status']['active_diagnoses'][0]['condition']
        symptoms = ', '.join(patient_profile['current_health_status']['active_symptoms'])
        medications = '\n'.join([f"- {med}" for med in patient_profile['current_medications']])
        doctor_name = patient_profile['primary_doctor']['name']
        allergies = ', '.join(patient_profile['allergies'])
        
        # Construct strict system prompt
        system_prompt = f"""You are a medical assistant for a patient. Provide helpful, accurate information based ONLY on the context below.

Patient Context:
- Name: {patient_profile['name']}
- Diagnosis: {diagnosis}
- Symptoms: {symptoms}
- Current Medications:
{medications}
- Allergies: {allergies}
- Primary Doctor: {doctor_name}

IMPORTANT RULES:
1. Base your answer ONLY on the patient context and general medical knowledge
2. Do NOT diagnose new conditions
3. Do NOT recommend changing medication dosages
4. Do NOT recommend stopping or substituting medications
5. For emergencies, tell the patient to call 911 or go to the ER
6. Keep responses concise (2-3 paragraphs maximum)
7. Always remind the patient to consult {doctor_name} for medical decisions

Patient Question: {user_message}

Answer:"""

        # Query the AI model
        payload = {
            "inputs": system_prompt,
            "parameters": {
                "max_new_tokens": 250,
                "temperature": 0.7,
                "top_p": 0.9,
                "do_sample": True,
                "return_full_text": False
            }
        }
        
        ai_result = query_ai_model(payload)
        
        # Handle API errors
        if ai_result.get('error'):
            return jsonify({
                'success': True,
                'response': f"⚠️ AI Model Unavailable: {ai_result['message']}\n\nIn the meantime, I can help with:\n• Medication information from your records\n• Dietary advice for {diagnosis}\n• General symptom information\n\nPlease try your question again, or contact {doctor_name} directly.",
                'type': 'error',
                'escalate': False
            })
        
        # Extract AI response
        ai_text = ai_result['text'].strip()
        
        # Safety check on AI response
        is_safe, warning = check_response_safety(ai_text)
        
        if not is_safe:
            return jsonify({
                'success': True,
                'response': warning,
                'type': 'safety_warning',
                'escalate': True
            })
        
        # Add disclaimer to AI response
        final_response = f"{ai_text}\n\n---\n*Generated by AI. Always consult {doctor_name} for medical advice.*"
        
        return jsonify({
            'success': True,
            'response': final_response,
            'type': 'ai_generated',
            'escalate': False
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error processing request: {str(e)}'
        }), 500

@app.route('/api/book', methods=['POST'])
def book_appointment():
    data = request.get_json()
    date = data.get('date')
    time = data.get('time')
    
    if not date or not time:
        return jsonify({'success': False, 'message': 'Date and time are required'}), 400
    
    # Check if slot is available
    if date in available_slots and time in available_slots[date]:
        # Remove the booked slot from available slots
        available_slots[date].remove(time)
        
        # Add to booked appointments
        appointment = {
            'date': date,
            'time': time,
            'doctor': 'Dr. Sarah Johnson',
            'specialty': 'General Practitioner',
            'booked_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        booked_appointments.append(appointment)
        
        return jsonify({
            'success': True, 
            'message': 'Appointment booked successfully!',
            'appointment': appointment
        })
    else:
        return jsonify({
            'success': False, 
            'message': 'Selected time slot is not available'
        }), 400

@app.route('/api/slots/<date>')
def get_slots(date):
    slots = available_slots.get(date, [])
    return jsonify({'date': date, 'slots': slots})

@app.route('/api/cancel/<int:appointment_index>', methods=['DELETE'])
def cancel_appointment(appointment_index):
    try:
        if 0 <= appointment_index < len(booked_appointments):
            # Get the appointment to cancel
            appointment = booked_appointments[appointment_index]
            date = appointment['date']
            time = appointment['time']
            
            # Remove the appointment
            booked_appointments.pop(appointment_index)
            
            # Add the time slot back to available slots
            if date in available_slots:
                if time not in available_slots[date]:
                    available_slots[date].append(time)
                    # Sort the time slots
                    available_slots[date].sort()
            else:
                available_slots[date] = [time]
            
            return jsonify({
                'success': True,
                'message': 'Appointment cancelled successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid appointment index'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

# Made with Bob
