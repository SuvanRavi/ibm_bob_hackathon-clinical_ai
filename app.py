from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

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
