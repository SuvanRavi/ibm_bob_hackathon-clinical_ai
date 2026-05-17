# Data Structure Documentation

## Overview
The application now uses JSON files to store and manage patient, doctor, and appointment data dynamically.

## JSON Data Files

### 1. `data/patients.json`
Stores patient information with the following structure:

```json
{
  "P001": {
    "patient_id": "P001",
    "patient_name": "John Anderson",
    "patient_age": 45,
    "blood_group": "O+",
    "contact_number": "+1 (555) 123-4567",
    "email": "john.anderson@email.com",
    "allergies": ["Penicillin", "Peanuts", "Latex"],
    "emergency_contact": {
      "name": "Sarah Anderson",
      "phone": "+1 (555) 987-6543",
      "relationship": "Spouse"
    },
    "appointment_details": [...],
    "symptom": "Persistent cough and mild fever",
    "prescription": [...],
    "diagnosis": "Upper respiratory tract infection"
  }
}
```

### 2. `data/doctors.json`
Stores doctor profiles:

```json
{
  "D001": {
    "doctor_id": "D001",
    "name": "Dr. Sarah Johnson",
    "specialty": "General Practitioner",
    "qualification": "MD, MBBS",
    "experience_years": 12,
    "contact": "+1 (555) 111-2222",
    "email": "s.johnson@medassistant.com",
    "available_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
    "consultation_fee": 150
  }
}
```

### 3. `data/appointments.json`
Stores appointment records:

```json
{
  "A001": {
    "appointment_id": "A001",
    "patient_id": "P001",
    "doctor_id": "D001",
    "date": "2026-05-17",
    "time": "10:00 AM",
    "status": "scheduled",
    "type": "follow-up",
    "notes": "Follow-up for respiratory infection",
    "booked_at": "2026-05-15 14:30:00"
  }
}
```

## How It Works

### Data Loading
- `app.py` loads all JSON files on startup using `load_json_data()` function
- Data is stored in memory: `patients_data`, `doctors_data`, `appointments_data`

### Current Patient
- The system uses `CURRENT_PATIENT_ID = 'P001'` to simulate a logged-in user
- In production, this would come from authentication/session management

### Helper Functions

1. **`get_current_patient()`** - Returns current patient's data
2. **`get_patient_appointments(patient_id)`** - Gets all scheduled appointments for a patient
3. **`get_medication_reminders(patient_id)`** - Extracts medication info from prescriptions
4. **`save_json_data(filename, data)`** - Saves updated data back to JSON files

### API Endpoints

#### Patient & Doctor APIs
- `GET /api/patient` - Get current patient information
- `GET /api/doctors` - Get all doctors
- `GET /api/doctors/<doctor_id>` - Get specific doctor details

#### Appointment APIs
- `POST /api/book` - Book new appointment (saves to JSON)
- `DELETE /api/cancel/<index>` - Cancel appointment (updates status to 'cancelled')
- `GET /api/slots/<date>` - Get available time slots

## Testing the Implementation

### 1. View Patient Profile
Navigate to: `http://localhost:5000/profile`
- Should display patient P001's information from JSON
- Shows name, age, blood group, allergies, medications

### 2. View Appointments
Navigate to: `http://localhost:5000/appointments`
- Should show scheduled appointments for patient P001
- Displays doctor name and specialty from doctors.json

### 3. Book New Appointment
Navigate to: `http://localhost:5000/schedule`
- Select a date and time
- Book appointment
- New appointment is saved to `data/appointments.json`

### 4. Cancel Appointment
From appointments page:
- Click "Cancel Appointment"
- Appointment status changes to 'cancelled' in JSON

## Benefits of This Approach

✅ **Dynamic Data**: All patient, doctor, and appointment info comes from JSON files
✅ **Easy Updates**: Modify JSON files to change data without touching code
✅ **Persistent Storage**: Bookings and cancellations are saved to files
✅ **Scalable**: Easy to add more patients, doctors, or appointments
✅ **Separation of Concerns**: Data is separate from application logic

## What's Still Hardcoded (By Design)

- UI labels and button text (e.g., "Submit", "Cancel")
- Navigation menu items
- Static instructions and disclaimers
- Available time slots (could be made dynamic in future)

These remain hardcoded because they are part of the UI design, not business data.