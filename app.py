from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import base64
import io
from PIL import Image
import os
import sys

# Add model directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'model'))

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Import inference service (will be loaded lazily)
inference_service = None

def get_inference_service():
    """Lazy load inference service"""
    global inference_service
    if inference_service is None:
        try:
            # Try to use pre-trained model first (no training required)
            from model.inference_pretrained import get_inference_service as get_service
            inference_service = get_service()
            print("✓ Symptom analyzer loaded (using pre-trained BioMedCLIP)")
        except Exception as e:
            print(f"⚠️ Warning: Could not load symptom analyzer: {e}")
            print("   Make sure dependencies are installed: pip install open-clip-torch")
            inference_service = False  # Mark as failed to avoid retrying
    return inference_service if inference_service is not False else None

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
    }
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

@app.route('/symptom-analyzer')
def symptom_analyzer():
    return render_template('symptom_analyzer.html')

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

@app.route('/api/analyze-symptom', methods=['POST'])
def analyze_symptom():
    """
    Analyze symptom from uploaded image
    
    Request body:
    {
        "image": "base64_encoded_image_string"
    }
    
    Response:
    {
        "success": true,
        "analysis": {
            "condition": "Melanocytic nevi",
            "confidence": 0.87,
            "severity": "mild",
            "severity_score": 1,
            "recommended_action": "...",
            "additional_notes": "...",
            "timestamp": "2026-05-16T16:40:00Z"
        }
    }
    """
    try:
        # Get inference service
        service = get_inference_service()
        
        if service is None:
            return jsonify({
                'success': False,
                'error': 'Symptom analyzer model not available',
                'message': 'The model has not been trained yet. Please train the model first using: python model/train_biomedclip.py'
            }), 503
        
        # Get request data
        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({
                'success': False,
                'error': 'No image provided',
                'message': 'Please provide an image in base64 format'
            }), 400
        
        # Decode base64 image
        try:
            image_data = data['image']
            
            # Remove data URL prefix if present
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            
            # Decode base64
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Validate image
            if image.mode not in ['RGB', 'RGBA']:
                image = image.convert('RGB')
            
            # Check image size (max 10MB)
            if len(image_bytes) > 10 * 1024 * 1024:
                return jsonify({
                    'success': False,
                    'error': 'Image too large',
                    'message': 'Image size must be less than 10MB'
                }), 400
                
        except Exception as e:
            return jsonify({
                'success': False,
                'error': 'Invalid image format',
                'message': f'Could not decode image: {str(e)}'
            }), 400
        
        # Perform analysis
        result = service.analyze_symptom(image)
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in analyze_symptom: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/api/symptom-analyzer/status', methods=['GET'])
def symptom_analyzer_status():
    """Check if symptom analyzer is available"""
    service = get_inference_service()
    
    return jsonify({
        'available': service is not None,
        'message': 'Symptom analyzer is ready' if service else 'Model not loaded. Please train the model first.'
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)

# Made with Bob
