"""
Response Templates
Pre-defined templates for common queries and responses
"""

from typing import Dict, List, Optional
from .config import DIETARY_GUIDELINES, MEDICATION_TIMING


class ResponseTemplates:
    """Provides response templates for common queries"""
    
    @staticmethod
    def medication_guidance(medication: Dict) -> str:
        """
        Generate medication guidance response
        
        Args:
            medication: Medication dictionary from patient data
            
        Returns:
            Formatted medication guidance
        """
        med_name = medication['medication']
        dosage = medication['dosage']
        duration = medication['duration']
        notes = medication.get('notes', '')
        
        response = f"**{med_name}**\n\n"
        response += f"📋 **Dosage**: {dosage}\n"
        response += f"⏱️ **Duration**: {duration}\n"
        
        if notes:
            response += f"📝 **Instructions**: {notes}\n\n"
            
            # Add timing guidance if available
            notes_lower = notes.lower()
            for timing_key, timing_info in MEDICATION_TIMING.items():
                if timing_key in notes_lower:
                    response += f"💡 **Timing Tip**: {timing_info}\n"
                    break
        
        response += "\n⚠️ **Important**: Take this medication exactly as prescribed. "
        response += "Do not stop or change the dosage without consulting your doctor."
        
        return response
    
    @staticmethod
    def dietary_advice(diagnosis: str, allergies: List[str]) -> str:
        """
        Generate dietary advice based on diagnosis
        
        Args:
            diagnosis: Patient's diagnosis
            allergies: List of patient's allergies
            
        Returns:
            Formatted dietary advice
        """
        # Normalize diagnosis for lookup
        diagnosis_lower = diagnosis.lower()
        
        # Find matching dietary guidelines
        guidelines = None
        for key in DIETARY_GUIDELINES.keys():
            if key in diagnosis_lower:
                guidelines = DIETARY_GUIDELINES[key]
                break
        
        if not guidelines:
            guidelines = DIETARY_GUIDELINES['default']
        
        response = f"**Dietary Recommendations for {diagnosis}**\n\n"
        
        # Recommended foods
        response += "✅ **Recommended Foods**:\n"
        for food in guidelines['recommended']:
            response += f"  • {food}\n"
        
        response += "\n❌ **Foods to Avoid**:\n"
        for food in guidelines['avoid']:
            response += f"  • {food}\n"
        
        # Add allergy warning
        if allergies:
            response += f"\n⚠️ **Allergy Alert**: Remember, you are allergic to: {', '.join(allergies)}\n"
            response += "Always check food labels and inform restaurants about your allergies.\n"
        
        response += "\n💡 **Note**: These are general guidelines. For personalized dietary advice, "
        response += "please consult with a nutritionist or your healthcare provider."
        
        return response
    
    @staticmethod
    def appointment_booking_nudge() -> str:
        """
        Generate appointment booking nudge
        
        Returns:
            Appointment booking suggestion
        """
        return (
            "📅 **Need to Schedule an Appointment?**\n\n"
            "You can easily book a follow-up appointment with your doctor:\n"
            "1. Select a convenient date and time from the available slots\n"
            "2. Confirm your booking\n"
            "3. Receive instant confirmation\n\n"
            "Would you like to schedule an appointment now? You can use the booking "
            "section on this page to select your preferred time slot."
        )
    
    @staticmethod
    def medication_list(prescriptions: List[Dict]) -> str:
        """
        Generate formatted medication list
        
        Args:
            prescriptions: List of prescription dictionaries
            
        Returns:
            Formatted medication list
        """
        if not prescriptions:
            return "You currently have no active prescriptions on file."
        
        response = "**Your Current Medications**\n\n"
        
        for i, med in enumerate(prescriptions, 1):
            response += f"{i}. **{med['medication']}**\n"
            response += f"   • Dosage: {med['dosage']}\n"
            response += f"   • Duration: {med['duration']}\n"
            if med.get('notes'):
                response += f"   • Instructions: {med['notes']}\n"
            response += "\n"
        
        response += "💊 Remember to take all medications as prescribed. "
        response += "If you have questions about any medication, please ask!"
        
        return response
    
    @staticmethod
    def allergy_information(allergies: List[str]) -> str:
        """
        Generate allergy information response
        
        Args:
            allergies: List of allergies
            
        Returns:
            Formatted allergy information
        """
        if not allergies:
            return "According to your medical records, you have no known allergies."
        
        response = "⚠️ **Your Allergy Information**\n\n"
        response += "You are allergic to:\n"
        
        for allergy in allergies:
            response += f"  • {allergy}\n"
        
        response += "\n**Important Safety Tips**:\n"
        response += "  • Always inform healthcare providers about your allergies\n"
        response += "  • Carry allergy information with you\n"
        response += "  • Read medication labels carefully\n"
        response += "  • Inform restaurants and food service staff\n"
        response += "  • Consider wearing a medical alert bracelet\n\n"
        response += "If you experience an allergic reaction, seek immediate medical attention."
        
        return response
    
    @staticmethod
    def general_health_tips() -> str:
        """
        Generate general health tips
        
        Returns:
            General health tips
        """
        return (
            "**General Health Tips**\n\n"
            "🏃 **Stay Active**: Aim for at least 30 minutes of moderate exercise daily\n\n"
            "💧 **Stay Hydrated**: Drink 8 glasses of water per day\n\n"
            "😴 **Get Adequate Sleep**: Aim for 7-9 hours of quality sleep\n\n"
            "🥗 **Eat Balanced Meals**: Include fruits, vegetables, whole grains, and lean proteins\n\n"
            "🧘 **Manage Stress**: Practice relaxation techniques like meditation or deep breathing\n\n"
            "📅 **Regular Check-ups**: Keep up with scheduled medical appointments\n\n"
            "💊 **Medication Adherence**: Take medications as prescribed\n\n"
            "Remember: These are general tips. Always follow your doctor's specific recommendations "
            "for your condition."
        )
    
    @staticmethod
    def greeting(patient_name: str) -> str:
        """
        Generate personalized greeting
        
        Args:
            patient_name: Patient's name
            
        Returns:
            Greeting message
        """
        return (
            f"Hello {patient_name}! 👋\n\n"
            "I'm your AI medical assistant. I can help you with:\n\n"
            "💊 **Medication Questions** - Information about your prescriptions\n"
            "🥗 **Dietary Advice** - Nutrition guidance based on your diagnosis\n"
            "📅 **Appointment Scheduling** - Help with booking follow-ups\n"
            "❓ **General Questions** - Post-consultation support\n\n"
            "How can I assist you today?"
        )
    
    @staticmethod
    def farewell() -> str:
        """
        Generate farewell message
        
        Returns:
            Farewell message
        """
        return (
            "Take care! 🌟\n\n"
            "Remember:\n"
            "• Take your medications as prescribed\n"
            "• Follow your doctor's recommendations\n"
            "• Contact your healthcare provider if you have concerns\n\n"
            "Feel free to ask me anything else anytime!"
        )
    
    @staticmethod
    def clarification_request() -> str:
        """
        Request clarification from user
        
        Returns:
            Clarification request message
        """
        return (
            "I want to make sure I understand your question correctly. "
            "Could you please provide more details or rephrase your question?\n\n"
            "For example:\n"
            "• 'When should I take my [medication name]?'\n"
            "• 'What foods should I eat with my condition?'\n"
            "• 'Can you explain my prescription?'"
        )
    
    @staticmethod
    def medication_reminder_setup() -> str:
        """
        Information about medication reminders
        
        Returns:
            Medication reminder information
        """
        return (
            "📱 **Medication Reminders**\n\n"
            "Your medication schedule is displayed on your dashboard. "
            "You can see:\n"
            "• Medication names and dosages\n"
            "• Scheduled times\n"
            "• Special instructions\n\n"
            "💡 **Tip**: Set phone alarms to help you remember your medication times!"
        )
    
    @staticmethod
    def symptom_worsening_response() -> str:
        """
        Response for worsening symptoms
        
        Returns:
            Worsening symptoms guidance
        """
        return (
            "⚠️ **Important: Worsening Symptoms**\n\n"
            "If your symptoms are worsening or you're experiencing new symptoms, "
            "please contact your doctor as soon as possible.\n\n"
            "**When to Seek Immediate Care**:\n"
            "• Severe pain or discomfort\n"
            "• Difficulty breathing\n"
            "• High fever (above 103°F/39.4°C)\n"
            "• Severe allergic reactions\n"
            "• Chest pain\n"
            "• Loss of consciousness\n\n"
            "For emergencies, call emergency services immediately."
        )
    
    @staticmethod
    def side_effects_response() -> str:
        """
        Response for medication side effects
        
        Returns:
            Side effects guidance
        """
        return (
            "💊 **Medication Side Effects**\n\n"
            "If you're experiencing side effects from your medication:\n\n"
            "1. **Don't stop taking the medication** without consulting your doctor\n"
            "2. **Document the side effects** - what, when, and how severe\n"
            "3. **Contact your doctor** to discuss the symptoms\n"
            "4. **Seek immediate care** if side effects are severe\n\n"
            "**Severe side effects requiring immediate attention**:\n"
            "• Difficulty breathing or swallowing\n"
            "• Severe rash or hives\n"
            "• Swelling of face, lips, or tongue\n"
            "• Chest pain or irregular heartbeat\n\n"
            "I'm unable to confidently answer this based on your medical records. "
            "Please consult your doctor for medical advice."
        )


# Made with Bob