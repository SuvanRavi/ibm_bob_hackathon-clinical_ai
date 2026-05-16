from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import base64
import io
from PIL import Image
import os
import sys
import json

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

# Load JSON data files
def load_json_data(filename):
    """Load data from JSON file"""
    try:
        filepath = os.path.join('data', filename)
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"⚠️ Warning: {filename} not found. Using empty data.")
        return {}
    except json.JSONDecodeError as e:
        print(f"⚠️ Warning: Error parsing {filename}: {e}")
        return {}

# Load data from JSON files
patients_data = load_json_data('patients.json')
doctors_data = load_json_data('doctors.json')
appointments_data = load_json_data('appointments.json')

# Current logged-in patient (for demo purposes)
CURRENT_PATIENT_ID = 'P001'

# Mock data for available time slots
available_slots = {
    '2026-05-17': ['09:00 AM', '11:00 AM', '02:00 PM', '03:00 PM', '04:00 PM'],
    '2026-05-18': ['09:00 AM', '10:00 AM', '11:00 AM', '02:00 PM', '03:00 PM'],
    '2026-05-19': ['09:00 AM', '11:00 AM', '03:00 PM', '04:00 PM'],
    '2026-05-20': ['10:00 AM', '11:00 AM', '02:00 PM', '03:00 PM', '04:00 PM'],
    '2026-05-21': ['09:00 AM', '10:00 AM', '02:00 PM', '03:00 PM'],
}

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

def get_current_patient():
    """Get current patient data"""
    return patients_data.get(CURRENT_PATIENT_ID, {})

def get_patient_appointments(patient_id):
    """Get all appointments for a patient"""
    patient_appointments = []
    for apt_id, apt in appointments_data.items():
        if apt['patient_id'] == patient_id and apt['status'] == 'scheduled':
            # Get doctor info
            doctor = doctors_data.get(apt['doctor_id'], {})
            patient_appointments.append({
                'appointment_id': apt_id,
                'date': apt['date'],
                'time': apt['time'],
                'doctor': doctor.get('name', 'Unknown Doctor'),
                'specialty': doctor.get('specialty', 'General'),
                'booked_at': apt['booked_at'],
                'notes': apt.get('notes', '')
            })
    return patient_appointments

def get_medication_reminders(patient_id):
    """Get medication reminders for a patient"""
    patient = patients_data.get(patient_id, {})
    prescriptions = patient.get('prescription', [])
    
    reminders = []
    for med in prescriptions:
        reminders.append({
            'medication': f"{med['medication']}",
            'time': '08:00 AM',  # Default time
            'frequency': med['dosage'],
            'notes': med.get('notes', '')
        })
    return reminders

@app.route('/')
def index():
    patient_appointments = get_patient_appointments(CURRENT_PATIENT_ID)
    medication_reminders = get_medication_reminders(CURRENT_PATIENT_ID)
    
    return render_template('schedule.html',
                         available_slots=available_slots,
                         booked_appointments=patient_appointments,
                         medication_reminders=medication_reminders,
                         upcoming_tasks=upcoming_tasks)

@app.route('/schedule')
def schedule():
    patient_appointments = get_patient_appointments(CURRENT_PATIENT_ID)
    medication_reminders = get_medication_reminders(CURRENT_PATIENT_ID)
    
    return render_template('schedule.html',
                         available_slots=available_slots,
                         booked_appointments=patient_appointments,
                         medication_reminders=medication_reminders,
                         upcoming_tasks=upcoming_tasks)

@app.route('/appointments')
def appointments():
    patient_appointments = get_patient_appointments(CURRENT_PATIENT_ID)
    return render_template('appointments.html',
                         booked_appointments=patient_appointments)

@app.route('/profile')
def profile():
    patient = get_current_patient()
    # Format patient data for template
    patient_profile = {
        'name': patient.get('patient_name', 'Unknown'),
        'age': patient.get('patient_age', 0),
        'blood_group': patient.get('blood_group', 'Unknown'),
        'contact_number': patient.get('contact_number', ''),
        'email': patient.get('email', ''),
        'allergies': patient.get('allergies', []),
        'current_medications': [f"{med['medication']} - {med['dosage']}"
                               for med in patient.get('prescription', [])],
        'emergency_contact': patient.get('emergency_contact', {})
    }
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
    doctor_id = data.get('doctor_id', 'D001')  # Default to first doctor
    
    if not date or not time:
        return jsonify({'success': False, 'message': 'Date and time are required'}), 400
    
    # Check if slot is available
    if date in available_slots and time in available_slots[date]:
        # Remove the booked slot from available slots
        available_slots[date].remove(time)
        
        # Generate new appointment ID
        new_apt_id = f"A{str(len(appointments_data) + 1).zfill(3)}"
        
        # Get doctor info
        doctor = doctors_data.get(doctor_id, {})
        
        # Create new appointment
        new_appointment = {
            'appointment_id': new_apt_id,
            'patient_id': CURRENT_PATIENT_ID,
            'doctor_id': doctor_id,
            'date': date,
            'time': time,
            'status': 'scheduled',
            'type': 'consultation',
            'notes': 'Scheduled via web portal',
            'booked_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Add to appointments data
        appointments_data[new_apt_id] = new_appointment
        
        # Save to JSON file
        save_json_data('appointments.json', appointments_data)
        
        # Return formatted appointment
        appointment = {
            'date': date,
            'time': time,
            'doctor': doctor.get('name', 'Unknown Doctor'),
            'specialty': doctor.get('specialty', 'General'),
            'booked_at': new_appointment['booked_at']
        }
        
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

def save_json_data(filename, data):
    """Save data to JSON file"""
    try:
        filepath = os.path.join('data', filename)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"⚠️ Error saving {filename}: {e}")
        return False

@app.route('/api/slots/<date>')
def get_slots(date):
    slots = available_slots.get(date, [])
    return jsonify({'date': date, 'slots': slots})

@app.route('/api/doctors', methods=['GET'])
def get_doctors():
    """Get all doctors"""
    doctors_list = [
        {
            'doctor_id': doc_id,
            'name': doc['name'],
            'specialty': doc['specialty'],
            'experience_years': doc.get('experience_years', 0),
            'consultation_fee': doc.get('consultation_fee', 0)
        }
        for doc_id, doc in doctors_data.items()
    ]
    return jsonify({'success': True, 'doctors': doctors_list})

@app.route('/api/doctors/<doctor_id>', methods=['GET'])
def get_doctor(doctor_id):
    """Get specific doctor details"""
    doctor = doctors_data.get(doctor_id)
    if doctor:
        return jsonify({'success': True, 'doctor': doctor})
    else:
        return jsonify({'success': False, 'message': 'Doctor not found'}), 404

@app.route('/api/patient', methods=['GET'])
def get_patient():
    """Get current patient information"""
    patient = get_current_patient()
    if patient:
        return jsonify({'success': True, 'patient': patient})
    else:
        return jsonify({'success': False, 'message': 'Patient not found'}), 404

@app.route('/api/cancel/<int:appointment_index>', methods=['DELETE'])
def cancel_appointment(appointment_index):
    try:
        # Get patient's appointments
        patient_appointments = get_patient_appointments(CURRENT_PATIENT_ID)
        
        if 0 <= appointment_index < len(patient_appointments):
            # Get the appointment to cancel
            appointment = patient_appointments[appointment_index]
            apt_id = appointment['appointment_id']
            date = appointment['date']
            time = appointment['time']
            
            # Update appointment status in data
            if apt_id in appointments_data:
                appointments_data[apt_id]['status'] = 'cancelled'
                save_json_data('appointments.json', appointments_data)
            
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
