# Symptom Analyzer Setup Instructions

This guide will help you set up and run the Symptom Analyzer feature with BioMedCLIP + LoRA fine-tuning.

## Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- NVIDIA GPU with CUDA support (recommended for training)
- At least 16GB RAM
- 20GB free disk space

## Step 1: Backend Setup

### 1.1 Create Python Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 1.2 Install Python Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- PyTorch and torchvision
- Transformers and PEFT (for LoRA)
- Open-CLIP (for BioMedCLIP)
- Flask and Flask-CORS
- PIL, pandas, scikit-learn

**Note**: Installation may take 10-15 minutes depending on your internet connection.

### 1.3 Download HAM10000 Dataset

The HAM10000 dataset must be downloaded manually:

**Option 1: Kaggle (Recommended)**
1. Go to: https://www.kaggle.com/datasets/kmader/skin-cancer-mnist-ham10000
2. Click "Download" (requires Kaggle account)
3. Extract the downloaded ZIP file
4. Place the contents in `data/ham10000/` directory

**Option 2: Official Source**
1. Go to: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/DBW86T
2. Download:
   - HAM10000_images_part_1.zip
   - HAM10000_images_part_2.zip
   - HAM10000_metadata.csv
3. Extract all files to `data/ham10000/`

**Expected Directory Structure:**
```
data/ham10000/
├── HAM10000_metadata.csv
├── HAM10000_images_part_1/
│   └── *.jpg (images)
└── HAM10000_images_part_2/
    └── *.jpg (images)
```

### 1.4 Train the Model

```bash
cd model
python train_biomedclip.py
```

**Training Details:**
- Duration: 2-4 hours on GPU (NVIDIA T4 or better)
- Duration: 8-12 hours on CPU (not recommended)
- Memory: ~8GB VRAM for GPU, 16GB RAM for CPU
- Output: Model checkpoint saved to `model/checkpoints/biomedclip_lora_final.pt`

**Training Progress:**
- You'll see epoch-by-epoch progress with loss and accuracy
- Best model is automatically saved
- Training history is saved to `model/checkpoints/training_history.json`

**If Training Fails:**
- Check GPU availability: `python -c "import torch; print(torch.cuda.is_available())"`
- Reduce batch size in `model/config.py` if out of memory
- Ensure dataset is properly downloaded and extracted

### 1.5 Test the Model (Optional)

```bash
cd model
python inference.py path/to/test/image.jpg
```

This will analyze a single image and display results.

## Step 2: Frontend Setup

### 2.1 Install Node Dependencies

```bash
cd frontend
npm install
```

### 2.2 Start Development Server

```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Step 3: Start Backend Server

In a new terminal (with virtual environment activated):

```bash
python app.py
```

The backend API will be available at `http://localhost:5000`

## Step 4: Access the Application

1. Open your browser to `http://localhost:5173`
2. Navigate to "Symptom Analyzer" in the top navigation
3. Upload an image of a skin condition
4. Click "Analyze Symptom"
5. View the AI-powered analysis results

## API Endpoints

### POST /api/analyze-symptom

Analyze a symptom from an uploaded image.

**Request:**
```json
{
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
}
```

**Response:**
```json
{
  "success": true,
  "analysis": {
    "condition": "Melanocytic nevi",
    "condition_code": "nv",
    "confidence": 0.87,
    "severity": "mild",
    "severity_score": 1,
    "recommended_action": "✓ MONITOR: This appears to be a benign condition...",
    "additional_notes": "Melanocytic nevi (moles) are usually benign...",
    "timestamp": "2026-05-16T16:40:00Z",
    "alternative_diagnoses": [
      {
        "condition": "Benign keratosis-like lesions",
        "confidence": 0.08
      }
    ]
  }
}
```

### GET /api/symptom-analyzer/status

Check if the symptom analyzer model is loaded and ready.

**Response:**
```json
{
  "available": true,
  "message": "Symptom analyzer is ready"
}
```

## Troubleshooting

### Model Not Loading

**Error:** "Symptom analyzer model not available"

**Solution:**
1. Ensure model training completed successfully
2. Check that `model/checkpoints/biomedclip_lora_final.pt` exists
3. Restart the Flask server

### CUDA Out of Memory

**Error:** "CUDA out of memory"

**Solution:**
1. Reduce `BATCH_SIZE` in `model/config.py` (try 8 or 4)
2. Close other GPU-intensive applications
3. Train on CPU (slower): Set `device = 'cpu'` in training script

### Dataset Not Found

**Error:** "Dataset not found"

**Solution:**
1. Verify dataset is in `data/ham10000/` directory
2. Check that `HAM10000_metadata.csv` exists
3. Ensure image directories are named correctly

### Frontend Can't Connect to Backend

**Error:** Network errors in browser console

**Solution:**
1. Ensure Flask server is running on port 5000
2. Check CORS is enabled (Flask-CORS installed)
3. Verify API_BASE_URL in `frontend/src/services/symptomAnalyzerService.ts`

### Low Confidence Predictions

**Issue:** Model returns low confidence scores

**Solution:**
1. Ensure image is clear and well-lit
2. Image should show the skin condition clearly
3. Try different angles or lighting
4. Model may need more training epochs

## Performance Optimization

### For Faster Training:
- Use a more powerful GPU (V100, A100)
- Increase `BATCH_SIZE` if you have more VRAM
- Reduce `NUM_EPOCHS` for quicker results (may reduce accuracy)

### For Faster Inference:
- Keep Flask server running (model loads once)
- Use GPU for inference if available
- Consider model quantization for production

## Model Configuration

Edit `model/config.py` to customize:

- `NUM_EPOCHS`: Number of training epochs (default: 10)
- `BATCH_SIZE`: Batch size for training (default: 16)
- `LEARNING_RATE`: Learning rate (default: 1e-4)
- `LORA_R`: LoRA rank (default: 8)
- `LORA_ALPHA`: LoRA alpha (default: 16)

## HAM10000 Classes

The model is trained to detect 7 skin conditions:

1. **Melanocytic nevi (nv)** - Benign moles (Mild)
2. **Melanoma (mel)** - Malignant skin cancer (Severe)
3. **Benign keratosis (bkl)** - Benign growths (Mild)
4. **Basal cell carcinoma (bcc)** - Common skin cancer (Severe)
5. **Actinic keratoses (akiec)** - Pre-cancerous lesions (Moderate)
6. **Vascular lesions (vasc)** - Blood vessel abnormalities (Moderate)
7. **Dermatofibroma (df)** - Benign skin growth (Mild)

## Security Considerations

- **File Upload Limits**: Max 10MB per image
- **File Type Validation**: Only JPEG and PNG accepted
- **Rate Limiting**: Consider adding rate limiting for production
- **HIPAA Compliance**: Ensure compliance if handling real patient data
- **Medical Disclaimer**: Always include disclaimer about AI limitations

## Next Steps

1. **Improve Model**: Train for more epochs or with data augmentation
2. **Add Features**: Support multiple image uploads, comparison views
3. **Integration**: Connect with appointment booking for severe cases
4. **Monitoring**: Add logging and analytics for model performance
5. **Deployment**: Deploy to cloud platform (AWS, Azure, GCP)

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review training logs in `model/checkpoints/`
3. Test with sample images from HAM10000 dataset
4. Verify all dependencies are installed correctly

## References

- BioMedCLIP Paper: https://arxiv.org/abs/2303.00915
- HAM10000 Dataset: https://doi.org/10.7910/DVN/DBW86T
- LoRA Paper: https://arxiv.org/abs/2106.09685
- Open-CLIP: https://github.com/mlfoundations/open_clip