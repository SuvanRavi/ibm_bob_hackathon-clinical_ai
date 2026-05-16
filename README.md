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
