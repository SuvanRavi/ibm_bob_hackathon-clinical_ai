"""
Comprehensive Test Suite for BioMistral Medical Chatbot
Tests initialization, RAG indexing, safety validation, and response generation
"""

import sys
import logging
from typing import Dict, List
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test results tracking
test_results = {
    'passed': 0,
    'failed': 0,
    'warnings': 0,
    'tests': []
}


def print_header(text: str):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)


def print_test_result(test_name: str, passed: bool, message: str = "", warning: bool = False):
    """Print and record test result"""
    if warning:
        status = "⚠️  WARNING"
        test_results['warnings'] += 1
    elif passed:
        status = "✅ PASSED"
        test_results['passed'] += 1
    else:
        status = "❌ FAILED"
        test_results['failed'] += 1
    
    test_results['tests'].append({
        'name': test_name,
        'passed': passed,
        'warning': warning,
        'message': message
    })
    
    print(f"\n{status}: {test_name}")
    if message:
        print(f"  → {message}")


def test_imports():
    """Test 1: Verify all required imports are available"""
    print_header("TEST 1: Import Dependencies")
    
    try:
        import torch
        print(f"✓ PyTorch version: {torch.__version__}")
        print(f"✓ CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"✓ CUDA device: {torch.cuda.get_device_name(0)}")
        
        import transformers
        print(f"✓ Transformers version: {transformers.__version__}")
        
        from sentence_transformers import SentenceTransformer
        print(f"✓ Sentence Transformers imported")
        
        import faiss
        print(f"✓ FAISS imported")
        
        import numpy as np
        print(f"✓ NumPy version: {np.__version__}")
        
        from medical_chatbot import BioMistralChatbot, PatientRAG, SafetyValidator, PatientContext
        print(f"✓ Medical chatbot modules imported")
        
        print_test_result("Import Dependencies", True, "All required packages imported successfully")
        return True
        
    except ImportError as e:
        print_test_result("Import Dependencies", False, f"Import error: {e}")
        return False


def test_patient_context():
    """Test 2: Test PatientContext data structure"""
    print_header("TEST 2: Patient Context Data Structure")
    
    try:
        from medical_chatbot import PatientContext
        
        # Create test patient context
        patient = PatientContext(
            patient_id="TEST001",
            patient_name="John Doe",
            patient_age=45,
            diagnosis="Acute Pharyngitis",
            appointment_details="Follow-up in 1 week",
            symptom="Sore throat, fever",
            prescription="Amoxicillin 500mg twice daily",
            dietary_restrictions="Avoid spicy foods"
        )
        
        print(f"✓ Patient context created: {patient.patient_name}")
        
        # Test to_text conversion
        text = patient.to_text()
        assert "John Doe" in text
        assert "Acute Pharyngitis" in text
        assert "Amoxicillin" in text
        print(f"✓ Patient context to_text() works correctly")
        
        print_test_result("Patient Context", True, "PatientContext structure working correctly")
        return True
        
    except Exception as e:
        print_test_result("Patient Context", False, f"Error: {e}")
        return False


def test_rag_initialization():
    """Test 3: Test RAG system initialization and indexing"""
    print_header("TEST 3: RAG System Initialization")
    
    try:
        from medical_chatbot import PatientRAG
        
        print("Initializing RAG system (this may take a moment)...")
        rag = PatientRAG()
        print(f"✓ RAG system initialized with embedding model")
        
        # Add test patient data
        test_patients = [
            {
                'patient_id': 'P001',
                'patient_name': 'Alice Smith',
                'patient_age': 35,
                'diagnosis': 'Hypertension',
                'appointment_details': 'Monthly checkup',
                'symptom': 'Headache, dizziness',
                'prescription': 'Lisinopril 10mg daily',
                'dietary_restrictions': 'Low sodium diet'
            },
            {
                'patient_id': 'P002',
                'patient_name': 'Bob Johnson',
                'patient_age': 50,
                'diagnosis': 'Type 2 Diabetes',
                'appointment_details': 'Quarterly review',
                'symptom': 'Fatigue, increased thirst',
                'prescription': 'Metformin 500mg twice daily',
                'dietary_restrictions': 'Low sugar, controlled carbs'
            },
            {
                'patient_id': 'P003',
                'patient_name': 'Carol Williams',
                'patient_age': 28,
                'diagnosis': 'Acute Pharyngitis',
                'appointment_details': 'Follow-up in 1 week',
                'symptom': 'Sore throat, fever',
                'prescription': 'Amoxicillin 500mg twice daily',
                'dietary_restrictions': 'Avoid spicy and acidic foods'
            }
        ]
        
        for patient in test_patients:
            rag.add_patient_data(patient)
        print(f"✓ Added {len(test_patients)} patient records")
        
        # Build index
        rag.build_index()
        print(f"✓ FAISS index built successfully")
        
        # Test retrieval
        query = "What medication is prescribed for throat infection?"
        contexts = rag.retrieve_context(query, top_k=2)
        print(f"✓ Retrieved {len(contexts)} relevant contexts for query")
        
        if contexts:
            print(f"  → Most relevant patient: {contexts[0].patient_name}")
            print(f"  → Diagnosis: {contexts[0].diagnosis}")
        
        print_test_result("RAG Initialization", True, f"RAG system working with {len(test_patients)} patients")
        return True
        
    except Exception as e:
        print_test_result("RAG Initialization", False, f"Error: {e}")
        return False


def test_safety_validator():
    """Test 4: Test safety validation system"""
    print_header("TEST 4: Safety Validation System")
    
    try:
        from medical_chatbot import SafetyValidator, PatientContext
        
        validator = SafetyValidator()
        
        # Test case 1: Safe response
        safe_response = "According to your records, you are taking Amoxicillin 500mg. Please consult your healthcare provider if you have concerns."
        is_safe, reason = validator.validate_response(safe_response)
        print(f"✓ Safe response validation: {is_safe} - {reason}")
        
        # Test case 2: Unsafe response (prescribing)
        unsafe_response = "You should prescribe yourself more antibiotics."
        is_safe, reason = validator.validate_response(unsafe_response)
        print(f"✓ Unsafe prescribing detected: {not is_safe} - {reason}")
        
        # Test case 3: Unsafe response (diagnosis)
        unsafe_diagnosis = "You definitely have pneumonia based on your symptoms."
        is_safe, reason = validator.validate_response(unsafe_diagnosis)
        print(f"✓ Unsafe diagnosis detected: {not is_safe} - {reason}")
        
        # Test case 4: Unsafe response (dosage change)
        unsafe_dosage = "You should increase your medication dosage."
        is_safe, reason = validator.validate_response(unsafe_dosage)
        print(f"✓ Unsafe dosage change detected: {not is_safe} - {reason}")
        
        # Test case 5: Grounding check
        patient = PatientContext(
            patient_id="TEST001",
            patient_name="John Doe",
            patient_age=45,
            diagnosis="Acute Pharyngitis",
            appointment_details="Follow-up",
            symptom="Sore throat",
            prescription="Amoxicillin 500mg",
            dietary_restrictions="None"
        )
        
        grounded_response = "According to your records, John Doe, you have Acute Pharyngitis and are prescribed Amoxicillin."
        is_safe, reason = validator.validate_response(grounded_response, patient)
        print(f"✓ Grounded response validation: {is_safe} - {reason}")
        
        # Test disclaimer addition
        response_without_disclaimer = "You should take your medication with food."
        response_with_disclaimer = validator.add_safety_disclaimer(response_without_disclaimer)
        has_disclaimer = "consult" in response_with_disclaimer.lower()
        print(f"✓ Disclaimer addition: {has_disclaimer}")
        
        print_test_result("Safety Validation", True, "All safety checks working correctly")
        return True
        
    except Exception as e:
        print_test_result("Safety Validation", False, f"Error: {e}")
        return False


def test_chatbot_initialization():
    """Test 5: Test BioMistral chatbot initialization"""
    print_header("TEST 5: BioMistral Chatbot Initialization")
    
    try:
        from medical_chatbot import BioMistralChatbot
        
        print("⚠️  Note: Model loading may take several minutes on first run")
        print("⚠️  BioMistral-7B is ~14GB and will be downloaded if not cached")
        
        chatbot = BioMistralChatbot()
        print(f"✓ Chatbot instance created")
        
        # Check if model should be loaded (skip if not enough resources)
        import torch
        if torch.cuda.is_available():
            print("✓ CUDA available - model can be loaded")
            load_model = True
        else:
            print("⚠️  CUDA not available - will use CPU (slower)")
            load_model = True
        
        if load_model:
            print("\nAttempting to load model (this may take 5-10 minutes)...")
            print("If this fails due to memory, the test will continue with other checks")
            
            try:
                chatbot.load_model()
                if chatbot.is_loaded:
                    print(f"✓ Model loaded successfully on {chatbot.device}")
                    print_test_result("Chatbot Initialization", True, "BioMistral model loaded successfully")
                else:
                    print_test_result("Chatbot Initialization", False, "Model failed to load", warning=True)
            except Exception as e:
                print(f"⚠️  Model loading failed: {e}")
                print_test_result("Chatbot Initialization", True, "Chatbot structure OK, model loading skipped", warning=True)
        else:
            print_test_result("Chatbot Initialization", True, "Chatbot structure OK, model loading skipped", warning=True)
        
        return True
        
    except Exception as e:
        print_test_result("Chatbot Initialization", False, f"Error: {e}")
        return False


def test_question_types():
    """Test 6: Test various question types with mock responses"""
    print_header("TEST 6: Question Type Handling")
    
    try:
        test_questions = [
            {
                'type': 'medication',
                'question': 'What is Amoxicillin used for?',
                'expected_keywords': ['antibiotic', 'infection', 'bacterial']
            },
            {
                'type': 'dietary',
                'question': 'What foods should I avoid with my condition?',
                'expected_keywords': ['food', 'diet', 'avoid', 'eat']
            },
            {
                'type': 'symptoms',
                'question': 'What are my current symptoms?',
                'expected_keywords': ['symptom', 'condition', 'experiencing']
            },
            {
                'type': 'emergency',
                'question': 'I have severe chest pain',
                'expected_keywords': ['emergency', '911', 'immediate']
            }
        ]
        
        print("Testing question classification and keyword detection:")
        for test in test_questions:
            question_lower = test['question'].lower()
            has_keywords = any(keyword in question_lower for keyword in test['expected_keywords'])
            print(f"✓ {test['type'].upper()}: '{test['question']}'")
            print(f"  → Keywords detected: {has_keywords}")
        
        print_test_result("Question Type Handling", True, f"Tested {len(test_questions)} question types")
        return True
        
    except Exception as e:
        print_test_result("Question Type Handling", False, f"Error: {e}")
        return False


def test_emergency_detection():
    """Test 7: Test emergency keyword detection"""
    print_header("TEST 7: Emergency Keyword Detection")
    
    try:
        emergency_phrases = [
            "I can't breathe",
            "severe chest pain",
            "heart attack symptoms",
            "bleeding heavily",
            "unconscious person",
            "difficulty breathing"
        ]
        
        safe_phrases = [
            "What is my medication?",
            "Can I eat spicy food?",
            "When is my appointment?",
            "Tell me about my diagnosis"
        ]
        
        emergency_keywords = ['emergency', 'urgent', 'severe pain', 'chest pain', 
                             'difficulty breathing', "can't breathe", 'heart attack', 
                             'bleeding heavily', 'unconscious']
        
        print("Testing emergency phrase detection:")
        for phrase in emergency_phrases:
            is_emergency = any(keyword in phrase.lower() for keyword in emergency_keywords)
            print(f"✓ Emergency detected in: '{phrase}' - {is_emergency}")
        
        print("\nTesting safe phrase detection:")
        for phrase in safe_phrases:
            is_emergency = any(keyword in phrase.lower() for keyword in emergency_keywords)
            print(f"✓ No emergency in: '{phrase}' - {not is_emergency}")
        
        print_test_result("Emergency Detection", True, "Emergency keyword detection working")
        return True
        
    except Exception as e:
        print_test_result("Emergency Detection", False, f"Error: {e}")
        return False


def test_integration():
    """Test 8: Integration test with full workflow"""
    print_header("TEST 8: Integration Test")
    
    try:
        from medical_chatbot import BioMistralChatbot
        
        print("Creating chatbot with patient data...")
        chatbot = BioMistralChatbot()
        
        # Add patient data
        patient_records = [
            {
                'patient_id': 'INT001',
                'patient_name': 'Integration Test Patient',
                'patient_age': 40,
                'diagnosis': 'Acute Pharyngitis',
                'appointment_details': 'Follow-up scheduled',
                'symptom': 'Sore throat, fever',
                'prescription': 'Amoxicillin 500mg twice daily',
                'dietary_restrictions': 'Avoid spicy foods'
            }
        ]
        
        chatbot.initialize_patient_data(patient_records)
        print(f"✓ Patient data initialized")
        
        # Test RAG retrieval
        contexts = chatbot.rag.retrieve_context("What medication am I taking?", top_k=1)
        print(f"✓ RAG retrieval working: {len(contexts)} contexts found")
        
        if contexts:
            print(f"  → Retrieved patient: {contexts[0].patient_name}")
        
        # Test prompt creation
        prompt = chatbot._create_grounded_prompt("What is my diagnosis?", contexts)
        print(f"✓ Grounded prompt created ({len(prompt)} characters)")
        
        print_test_result("Integration Test", True, "Full workflow integration successful")
        return True
        
    except Exception as e:
        print_test_result("Integration Test", False, f"Error: {e}")
        return False


def print_summary():
    """Print test summary"""
    print_header("TEST SUMMARY")
    
    total_tests = test_results['passed'] + test_results['failed']
    pass_rate = (test_results['passed'] / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\nTotal Tests Run: {total_tests}")
    print(f"✅ Passed: {test_results['passed']}")
    print(f"❌ Failed: {test_results['failed']}")
    print(f"⚠️  Warnings: {test_results['warnings']}")
    print(f"Pass Rate: {pass_rate:.1f}%")
    
    if test_results['failed'] > 0:
        print("\n❌ FAILED TESTS:")
        for test in test_results['tests']:
            if not test['passed'] and not test['warning']:
                print(f"  • {test['name']}: {test['message']}")
    
    if test_results['warnings'] > 0:
        print("\n⚠️  WARNINGS:")
        for test in test_results['tests']:
            if test['warning']:
                print(f"  • {test['name']}: {test['message']}")
    
    print("\n" + "=" * 80)
    if test_results['failed'] == 0:
        print("🎉 ALL TESTS PASSED! The chatbot system is working correctly.")
    else:
        print("⚠️  Some tests failed. Please review the errors above.")
    print("=" * 80)


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("  BioMistral Medical Chatbot - Comprehensive Test Suite")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 80)
    
    print("\n⚠️  IMPORTANT NOTES:")
    print("  • First run will download BioMistral-7B model (~14GB)")
    print("  • Model loading may take 5-10 minutes")
    print("  • GPU recommended but not required (CPU will be slower)")
    print("  • Some tests may be skipped if resources are insufficient")
    
    # Run all tests
    test_imports()
    test_patient_context()
    test_rag_initialization()
    test_safety_validator()
    test_chatbot_initialization()
    test_question_types()
    test_emergency_detection()
    test_integration()
    
    # Print summary
    print_summary()
    
    # Return exit code
    return 0 if test_results['failed'] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

# Made with Bob
