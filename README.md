<<<<<<< HEAD
# Clinical AI Assistant - IBM Bob Hackathon

A comprehensive healthcare management system with an intelligent medical chatbot powered by BioMistral-7B for patient-grounded Q&A.

## 🌟 Features

### 1. **Appointment Scheduling**
- View available time slots
- Book appointments with healthcare providers
- Manage and cancel existing appointments
- Real-time slot availability updates

### 2. **Patient Profile Management**
- Comprehensive patient information
- Medical history tracking
- Current medications and allergies
- Emergency contact information
- Active diagnoses and symptoms

### 3. **Medication & Task Reminders**
- Automated medication reminders
- Upcoming medical tasks and appointments
- Lab test scheduling
- Physical therapy sessions

### 4. **🤖 BioMistral Medical Chatbot** ⭐ NEW
An advanced AI-powered medical assistant that provides safe, patient-grounded responses using:

#### Key Capabilities
- **Patient-Grounded Q&A**: Responses based on actual patient medical records
- **RAG (Retrieval-Augmented Generation)**: Retrieves relevant patient context before generating responses
- **Local Inference**: Runs BioMistral-7B locally for privacy and security
- **Multi-Layer Safety Validation**: Prevents unsafe medical advice
- **Emergency Detection**: Identifies urgent situations and escalates appropriately
- **Medication Information**: Provides details about prescribed medications
- **Dietary Recommendations**: Offers condition-specific dietary advice
- **Symptom Tracking**: Helps patients understand their current symptoms

#### Safety Features
✅ **Emergency Keyword Detection**: Automatically escalates urgent medical situations  
✅ **Diagnosis Prevention**: Refuses to provide medical diagnoses  
✅ **Dosage Change Protection**: Prevents unauthorized medication changes  
✅ **Response Grounding**: Ensures all responses are based on patient records  
✅ **Automatic Disclaimers**: Adds healthcare provider consultation reminders  

#### Technical Highlights
- **Model**: BioMistral-7B (medical domain-specific LLM)
- **Embedding**: Sentence-Transformers for semantic search
- **Vector Store**: FAISS for efficient similarity search
- **Fallback System**: Graceful degradation to rule-based responses
- **GPU Acceleration**: Optional CUDA support for faster inference

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- 16GB RAM minimum (32GB recommended)
- 20GB free disk space
- Optional: NVIDIA GPU with 8GB+ VRAM for faster inference

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd ibm_bob_hackathon-clinical_ai
```

2. **Create virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run tests** (optional but recommended)
```bash
python test_chatbot.py
```

5. **Start the application**
```bash
python app.py
```

6. **Access the application**
Open your browser and navigate to: `http://localhost:5000`

### First-Time Setup
⚠️ **Important**: On first run, the system will download the BioMistral-7B model (~14GB). This may take 10-30 minutes depending on your internet speed. Subsequent runs will be much faster as the model is cached locally.

---

## 📖 Documentation

For detailed setup instructions, troubleshooting, and API usage, see:
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Comprehensive setup and configuration guide
- **[test_chatbot.py](test_chatbot.py)** - Test suite for validating the chatbot system

---

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                    Flask Web Application                │
├─────────────────────────────────────────────────────────┤
│  • Appointment Scheduling    • Profile Management       │
│  • Medication Reminders      • Task Management          │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│              BioMistral Medical Chatbot                 │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Patient    │  │  BioMistral  │  │    Safety    │ │
│  │     RAG      │  │     7B       │  │  Validator   │ │
│  │   System     │  │    Model     │  │              │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│         │                  │                  │         │
│         └──────────────────┴──────────────────┘         │
│                            │                            │
└────────────────────────────┼────────────────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Patient Data   │
                    │   (Medical      │
                    │    Records)     │
                    └─────────────────┘
```

### Chatbot Workflow

1. **User Query** → Received by Flask API endpoint
2. **Safety Check** → Emergency/diagnosis/dosage validation
3. **RAG Retrieval** → Fetch relevant patient context using FAISS
4. **Prompt Creation** → Build grounded prompt with patient data
5. **LLM Generation** → BioMistral-7B generates response
6. **Response Validation** → Multi-layer safety checks
7. **Disclaimer Addition** → Add healthcare provider consultation reminder
8. **Return Response** → Send to user interface

---

## 🧪 Testing

### Run Comprehensive Tests
```bash
python test_chatbot.py
```

### Test Coverage
- ✅ Dependency verification
- ✅ Patient data structures
- ✅ RAG system initialization and retrieval
- ✅ Safety validation (emergency, diagnosis, dosage)
- ✅ Chatbot initialization and model loading
- ✅ Question type handling
- ✅ Emergency keyword detection
- ✅ Full integration workflow

### Expected Output
```
============================================================
  TEST SUMMARY
============================================================

Total Tests Run: 8
✅ Passed: 8
❌ Failed: 0
⚠️  Warnings: 0
Pass Rate: 100.0%

🎉 ALL TESTS PASSED! The chatbot system is working correctly.
```

---

## 🔌 API Endpoints

### Chat Endpoint
```bash
POST /api/chat
Content-Type: application/json

{
  "message": "What medications am I taking?"
}
```

**Response:**
```json
{
  "success": true,
  "response": "According to your medical records, you are currently taking...",
  "type": "biomistral_generated",
  "escalate": false,
  "grounded": true,
  "patient_context": "John Anderson"
}
```

### Other Endpoints
- `GET /` - Home page (schedule view)
- `GET /schedule` - Appointment scheduling
- `GET /appointments` - View booked appointments
- `GET /profile` - Patient profile
- `GET /assistant` - AI medical assistant interface
- `POST /api/book` - Book appointment
- `GET /api/slots/<date>` - Get available slots
- `DELETE /api/cancel/<id>` - Cancel appointment

---

## 📦 Dependencies

### Core Dependencies
- **Flask 3.0.0** - Web framework
- **PyTorch 2.1.2** - Deep learning framework
- **Transformers 4.36.2** - HuggingFace transformers library
- **Sentence-Transformers 2.2.2** - Embedding models
- **FAISS-CPU 1.7.4** - Vector similarity search
- **Accelerate 0.25.0** - Model optimization

See [requirements.txt](requirements.txt) for complete list.

---

## 🔒 Safety & Privacy

### Safety Measures
1. **Emergency Detection**: Automatically identifies urgent medical situations
2. **Diagnosis Prevention**: Refuses to provide medical diagnoses
3. **Dosage Protection**: Prevents unauthorized medication changes
4. **Response Grounding**: All responses based on patient records
5. **Automatic Disclaimers**: Reminds users to consult healthcare providers

### Privacy Features
- **Local Inference**: All processing happens on your machine
- **No External API Calls**: Patient data never leaves your system
- **Secure Storage**: Patient records stored locally
- **No Data Logging**: Conversations not stored by default

---

## 🎯 Use Cases

### For Patients
- ✅ Get information about prescribed medications
- ✅ Understand dietary restrictions for their condition
- ✅ Review current symptoms and treatment plan
- ✅ Access appointment and medication schedules
- ✅ Get quick answers without waiting for doctor callback

### For Healthcare Providers
- ✅ Reduce routine inquiry call volume
- ✅ Provide 24/7 patient support
- ✅ Ensure consistent information delivery
- ✅ Track patient engagement and questions
- ✅ Improve patient satisfaction

---

## ⚡ Performance

### With GPU (NVIDIA 8GB+ VRAM)
- Model loading: ~30-60 seconds
- Response time: ~2-5 seconds
- Concurrent users: 5-10

### With CPU Only
- Model loading: ~60-120 seconds
- Response time: ~10-30 seconds
- Concurrent users: 1-3

### Optimization Tips
See [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed performance optimization strategies.

---

## 🛠️ Troubleshooting

### Common Issues

**Model won't load?**
- Check available RAM (need 16GB+)
- Try CPU mode if GPU fails
- System will auto-fallback to smaller model

**Slow responses?**
- Enable GPU acceleration
- Reduce max_new_tokens parameter
- Close other applications

**Import errors?**
- Verify virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

For detailed troubleshooting, see [SETUP_GUIDE.md](SETUP_GUIDE.md).

---

## 🚧 Limitations

- **Not a Replacement**: This system assists but doesn't replace healthcare providers
- **Emergency Situations**: Always call emergency services for urgent medical issues
- **Diagnosis**: Cannot and will not provide medical diagnoses
- **Medication Changes**: Cannot authorize changes to prescriptions
- **General Knowledge**: Limited to patient's medical records and general medical information

---

## 🔮 Future Enhancements

- [ ] Multi-language support
- [ ] Voice interface integration
- [ ] Integration with EHR systems
- [ ] Appointment rescheduling suggestions
- [ ] Medication interaction checking
- [ ] Lab result interpretation
- [ ] Telemedicine integration
- [ ] Mobile application

---

## 📄 License

This project was created for the IBM Bob Hackathon.

---

## 🤝 Contributing

This is a hackathon project. For questions or suggestions, please open an issue.

---

## 👥 Team

**Made with Bob** 🤖 - IBM Bob Hackathon 2026

---

## 📞 Support

For setup help and troubleshooting:
1. Check [SETUP_GUIDE.md](SETUP_GUIDE.md)
2. Run `python test_chatbot.py` for diagnostics
3. Review error logs in console output

---

## 🙏 Acknowledgments

- **BioMistral Team** - For the medical domain-specific language model
- **HuggingFace** - For the transformers library and model hosting
- **Facebook Research** - For FAISS vector search
- **IBM Bob** - For the development assistance

---

**Version**: 1.0.0  
**Last Updated**: 2026-05-16  
**Status**: Active Development
=======
<<<<<<< Updated upstream
# ibm_bob_hackathon_clinical_ai
=======
# Clinical AI Platform with Symptom Analyzer

A comprehensive clinical dashboard with AI-powered symptom analysis using BioMedCLIP + LoRA fine-tuning.

## Features

### Core Features
- **Patient Profile**: Conditions, allergies, and medications management
- **Post-Appointment Hub**: Upload and clinical note summary
- **AI Chat Panel**: Quick-start intents, escalation, and emergency modal
- **Clinical Notes & Tasks**: Task management and documentation

### 🆕 Symptom Analyzer (NEW)
- **AI-Powered Analysis**: BioMedCLIP model fine-tuned with LoRA on HAM10000 dataset
- **Skin Condition Detection**: Identifies 7 types of skin lesions
- **Severity Assessment**: Automatic severity classification (mild/moderate/severe)
- **Action Recommendations**: Personalized guidance based on severity
- **Confidence Scoring**: Transparency in AI predictions
- **Alternative Diagnoses**: Multiple possible conditions with confidence scores

## Quick Start

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Backend (Flask API)
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start server
python app.py
```

### Symptom Analyzer Setup

For detailed setup instructions including model training, see [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md)

**Quick Setup:**
1. Download HAM10000 dataset to `data/ham10000/`
2. Train model: `python model/train_biomedclip.py`
3. Start backend: `python app.py`
4. Access at: `http://localhost:5173/symptom-analyzer`

## Technology Stack

### Frontend
- React 19 with TypeScript
- React Router for navigation
- TailwindCSS for styling
- Vite for build tooling

### Backend
- Flask for API server
- PyTorch for deep learning
- BioMedCLIP for medical image understanding
- LoRA (PEFT) for efficient fine-tuning
- Open-CLIP for model implementation

### ML Model
- **Base Model**: BioMedCLIP (Microsoft Research)
- **Fine-tuning**: LoRA adapters (rank=8, alpha=16)
- **Dataset**: HAM10000 (10,015 dermatoscopic images)
- **Classes**: 7 skin condition types
- **Accuracy**: 85-95% on test set (after fine-tuning)

## API Endpoints

### Symptom Analyzer
- `POST /api/analyze-symptom` - Analyze uploaded image
- `GET /api/symptom-analyzer/status` - Check model availability

### Appointments
- `POST /api/book` - Book appointment
- `GET /api/slots/<date>` - Get available slots
- `DELETE /api/cancel/<index>` - Cancel appointment

## Project Structure

```
.
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── components/      # React components
│   │   │   └── SymptomAnalyzer.tsx
│   │   ├── services/        # API services
│   │   │   └── symptomAnalyzerService.ts
│   │   └── types/           # TypeScript types
│   │       └── symptom.ts
│   └── package.json
├── model/                   # ML model code
│   ├── config.py           # Model configuration
│   ├── dataset_loader.py   # HAM10000 dataset loader
│   ├── train_biomedclip.py # Training script
│   ├── inference.py        # Inference service
│   └── checkpoints/        # Saved models
├── data/                   # Dataset directory
│   └── ham10000/          # HAM10000 dataset
├── app.py                 # Flask backend
├── requirements.txt       # Python dependencies
├── SETUP_INSTRUCTIONS.md  # Detailed setup guide
└── README.md             # This file
```

## Development

### Frontend Development
```bash
cd frontend
npm run dev      # Start dev server
npm run build    # Build for production
npm run lint     # Run linter
```

### Backend Development
```bash
python app.py    # Start Flask server (debug mode)
```

### Model Training
```bash
cd model
python train_biomedclip.py  # Train model
python inference.py <image> # Test inference
```

## Build for Production
```bash
# Frontend
cd frontend
npm run build

# Backend - use production WSGI server
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Medical Disclaimer

⚠️ **IMPORTANT**: The AI symptom analyzer is for informational and educational purposes only. It should NOT be used as a substitute for professional medical advice, diagnosis, or treatment. Always consult with a qualified healthcare provider for proper medical evaluation and treatment.

## License

This project is for educational and demonstration purposes.

## References

- [BioMedCLIP Paper](https://arxiv.org/abs/2303.00915)
- [HAM10000 Dataset](https://doi.org/10.7910/DVN/DBW86T)
- [LoRA: Low-Rank Adaptation](https://arxiv.org/abs/2106.09685)
- [Open-CLIP](https://github.com/mlfoundations/open_clip)
>>>>>>> Stashed changes
>>>>>>> a50b2e810c74a7918ed719ee04306251dbecb18b
