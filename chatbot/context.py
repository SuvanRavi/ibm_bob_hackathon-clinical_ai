"""
Patient Context Retriever
Extracts and formats patient medical information for chatbot context
"""

import json
import os
from typing import Dict, List, Optional, Any


class PatientContextRetriever:
    """Retrieves and formats patient medical context from JSON data"""
    
    def __init__(self, patients_data_path: str = 'data/patients.json'):
        """
        Initialize context retriever
        
        Args:
            patients_data_path: Path to patients.json file
        """
        self.patients_data_path = patients_data_path
        self.patients_data = self._load_patients_data()
    
    def _load_patients_data(self) -> Dict:
        """Load patients data from JSON file"""
        try:
            with open(self.patients_data_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️ Warning: {self.patients_data_path} not found")
            return {}
        except json.JSONDecodeError as e:
            print(f"⚠️ Warning: Error parsing {self.patients_data_path}: {e}")
            return {}
    
    def get_patient_context(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """
        Get complete patient context
        
        Args:
            patient_id: Patient ID (e.g., 'P001')
            
        Returns:
            Dictionary with patient context or None if not found
        """
        patient = self.patients_data.get(patient_id)
        
        if not patient:
            return None
        
        return {
            'patient_id': patient.get('patient_id'),
            'patient_name': patient.get('patient_name'),
            'patient_age': patient.get('patient_age'),
            'blood_group': patient.get('blood_group'),
            'allergies': patient.get('allergies', []),
            'current_symptom': patient.get('symptom'),
            'diagnosis': patient.get('diagnosis'),
            'prescriptions': patient.get('prescription', []),
            'emergency_contact': patient.get('emergency_contact', {})
        }
    
    def get_formatted_context(self, patient_id: str) -> str:
        """
        Get formatted patient context as a string for LLM
        
        Args:
            patient_id: Patient ID
            
        Returns:
            Formatted context string
        """
        context = self.get_patient_context(patient_id)
        
        if not context:
            return "No patient data available."
        
        # Format prescriptions
        prescriptions_text = ""
        if context['prescriptions']:
            prescriptions_list = []
            for med in context['prescriptions']:
                med_text = f"  - {med['medication']}: {med['dosage']}, {med['duration']}"
                if med.get('notes'):
                    med_text += f" ({med['notes']})"
                prescriptions_list.append(med_text)
            prescriptions_text = "\n".join(prescriptions_list)
        else:
            prescriptions_text = "  None"
        
        # Format allergies
        allergies_text = ", ".join(context['allergies']) if context['allergies'] else "None"
        
        formatted = f"""
PATIENT MEDICAL CONTEXT:

Patient Information:
- Name: {context['patient_name']}
- Age: {context['patient_age']} years
- Blood Group: {context['blood_group']}

Allergies: {allergies_text}

Current Diagnosis: {context['diagnosis']}

Current Symptoms: {context['current_symptom']}

Current Prescriptions:
{prescriptions_text}

IMPORTANT: Only provide information based on this medical context. Do not invent or assume any medical information not explicitly stated above.
"""
        return formatted.strip()
    
    def get_prescriptions(self, patient_id: str) -> List[Dict]:
        """
        Get patient's current prescriptions
        
        Args:
            patient_id: Patient ID
            
        Returns:
            List of prescription dictionaries
        """
        context = self.get_patient_context(patient_id)
        return context['prescriptions'] if context else []
    
    def get_allergies(self, patient_id: str) -> List[str]:
        """
        Get patient's allergies
        
        Args:
            patient_id: Patient ID
            
        Returns:
            List of allergies
        """
        context = self.get_patient_context(patient_id)
        return context['allergies'] if context else []
    
    def get_diagnosis(self, patient_id: str) -> Optional[str]:
        """
        Get patient's current diagnosis
        
        Args:
            patient_id: Patient ID
            
        Returns:
            Diagnosis string or None
        """
        context = self.get_patient_context(patient_id)
        return context['diagnosis'] if context else None
    
    def find_medication(self, patient_id: str, medication_name: str) -> Optional[Dict]:
        """
        Find a specific medication in patient's prescriptions
        
        Args:
            patient_id: Patient ID
            medication_name: Name of medication to find (case-insensitive)
            
        Returns:
            Medication dictionary or None if not found
        """
        prescriptions = self.get_prescriptions(patient_id)
        medication_name_lower = medication_name.lower()
        
        for med in prescriptions:
            if medication_name_lower in med['medication'].lower():
                return med
        
        return None
    
    def has_allergy(self, patient_id: str, substance: str) -> bool:
        """
        Check if patient has a specific allergy
        
        Args:
            patient_id: Patient ID
            substance: Substance to check (case-insensitive)
            
        Returns:
            True if patient has the allergy, False otherwise
        """
        allergies = self.get_allergies(patient_id)
        substance_lower = substance.lower()
        
        return any(substance_lower in allergy.lower() for allergy in allergies)
    
    def get_medication_summary(self, patient_id: str) -> str:
        """
        Get a formatted summary of patient's medications
        
        Args:
            patient_id: Patient ID
            
        Returns:
            Formatted medication summary
        """
        prescriptions = self.get_prescriptions(patient_id)
        
        if not prescriptions:
            return "You currently have no active prescriptions."
        
        summary = "Your current medications:\n\n"
        for i, med in enumerate(prescriptions, 1):
            summary += f"{i}. **{med['medication']}**\n"
            summary += f"   - Dosage: {med['dosage']}\n"
            summary += f"   - Duration: {med['duration']}\n"
            if med.get('notes'):
                summary += f"   - Instructions: {med['notes']}\n"
            summary += "\n"
        
        return summary.strip()
    
    def get_allergy_warning(self, patient_id: str) -> str:
        """
        Get formatted allergy warning
        
        Args:
            patient_id: Patient ID
            
        Returns:
            Formatted allergy warning or empty string
        """
        allergies = self.get_allergies(patient_id)
        
        if not allergies:
            return ""
        
        return f"⚠️ **Allergy Alert**: You are allergic to: {', '.join(allergies)}"
    
    def validate_patient_exists(self, patient_id: str) -> bool:
        """
        Check if patient exists in database
        
        Args:
            patient_id: Patient ID
            
        Returns:
            True if patient exists, False otherwise
        """
        return patient_id in self.patients_data


# Global instance (singleton pattern)
_context_retriever = None


def get_context_retriever() -> PatientContextRetriever:
    """Get or create context retriever instance"""
    global _context_retriever
    
    if _context_retriever is None:
        _context_retriever = PatientContextRetriever()
    
    return _context_retriever


# Made with Bob