# BioMistral Medical Chatbot - Setup Guide

## 📋 Table of Contents
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [First-Time Setup](#first-time-setup)
- [Testing the Chatbot](#testing-the-chatbot)
- [API Usage](#api-usage)
- [Troubleshooting](#troubleshooting)
- [Performance Optimization](#performance-optimization)

---

## 🖥️ System Requirements

### Minimum Requirements
- **Operating System**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **Python**: 3.8 or higher (3.9-3.11 recommended)
- **RAM**: 16GB minimum (32GB recommended for optimal performance)
- **Storage**: 20GB free space (for model downloads and cache)
- **Internet**: Required for initial model download (~14GB)

### Optional but Recommended
- **GPU**: NVIDIA GPU with 8GB+ VRAM (for faster inference)
  - CUDA 11.8 or higher
  - cuDNN 8.x
- **CPU**: Multi-core processor (8+ cores recommended for CPU inference)

### GPU vs CPU Performance
- **With GPU**: Response time ~2-5 seconds
- **Without GPU (CPU only)**: Response time ~10-30 seconds
- The system works on both, but GPU significantly improves user experience

---

## 📦 Installation

### Step 1: Clone or Download the Repository
```bash
git clone <repository-url>
cd ibm_bob_hackathon-clinical_ai
```

### Step 2: Create a Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Note**: Installation may take 5-10 minutes depending on your internet speed.

### Step 4: Verify Installation
Run the test script to verify all dependencies are installed correctly:
```bash
python test_chatbot.py
```

---

## 🚀 Running the Application

### Start the Flask Server
```bash
python app.py
```

You should see output similar to:
```
============================================================
🚀 Clinical AI Assistant - BioMistral Local Inference
============================================================
🤖 Loading BioMistral-7B model for medical Q&A...
⚕️  Patient-grounded responses with RAG
🔒 Multi-layer safety validation enabled
============================================================
INFO:medical_chatbot:Initializing BioMistral chatbot...
INFO:medical_chatbot:Loading BioMistral model: BioMistral/BioMistral-7B
```

### Access the Application
Open your web browser and navigate to:
```
http://localhost:5000
```

---

## 🎯 First-Time Setup

### Model Download Behavior
**IMPORTANT**: On first run, the system will download the BioMistral-7B model (~14GB).

#### What to Expect:
1. **Download Time**: 10-30 minutes (depending on internet speed)
2. **Storage Location**: Models are cached in:
   - Windows: `C:\Users\<username>\.cache\huggingface\hub\`
   - macOS/Linux: `~/.cache/huggingface/hub/`
3. **Progress**: You'll see download progress in the terminal
4. **Subsequent Runs**: Model loads from cache (much faster, ~30-60 seconds)

#### First Run Output Example:
```
INFO:transformers:Downloading model...
Downloading: 100%|████████████████| 14.2GB/14.2GB [15:23<00:00, 15.4MB/s]
INFO:medical_chatbot:BioMistral model loaded successfully
```

### Fallback Model
If BioMistral-7B fails to load (due to memory constraints), the system automatically falls back to:
- **BioGPT-Large** (~1.5GB, less capable but more resource-friendly)
- Or rule-based responses (no model required)

---

## 🧪 Testing the Chatbot

### Run Comprehensive Tests
```bash
python test_chatbot.py
```

### Test Output
The test script will:
1. ✅ Verify all dependencies are installed
2. ✅ Test patient data structures
3. ✅ Test RAG (Retrieval-Augmented Generation) system
4. ✅ Test safety validation
5. ✅ Test chatbot initialization
6. ✅ Test question type handling
7. ✅ Test emergency detection
8. ✅ Run integration tests

### Expected Test Results
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

## 🔌 API Usage

### Chat Endpoint

#### Request
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What medications am I taking?"}'
```

#### Response
```json
{
  "success": true,
  "response": "According to your medical records, you are currently taking:\n• Amoxicillin 500mg - Twice daily\n• Vitamin D3 - Once daily\n• Lisinopril 10mg - Once daily\n\nNote: This information is based on your medical records. Always consult your healthcare provider for medical decisions.",
  "type": "biomistral_generated",
  "escalate": false,
  "grounded": true,
  "patient_context": "John Anderson"
}
```

### Python Example
```python
import requests

url = "http://localhost:5000/api/chat"
data = {"message": "What should I eat with my condition?"}

response = requests.post(url, json=data)
result = response.json()

print(result['response'])
```

### JavaScript Example
```javascript
fetch('http://localhost:5000/api/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    message: 'What are my current symptoms?'
  })
})
.then(response => response.json())
.then(data => console.log(data.response));
```

---

## 🔧 Troubleshooting

### Issue 1: Model Loading Fails

#### Symptom
```
Error loading BioMistral model: CUDA out of memory
```

#### Solutions
1. **Use CPU instead of GPU**:
   ```python
   # In medical_chatbot.py, modify initialization:
   chatbot = BioMistralChatbot(device="cpu")
   ```

2. **Reduce batch size** (if applicable)

3. **Close other applications** to free up memory

4. **Use fallback model** (automatic, but you can force it):
   ```python
   chatbot._load_fallback_model()
   ```

### Issue 2: Slow Response Times

#### Symptom
Responses take 30+ seconds

#### Solutions
1. **Check if GPU is being used**:
   ```python
   import torch
   print(torch.cuda.is_available())  # Should be True
   ```

2. **Install CUDA-enabled PyTorch**:
   ```bash
   pip uninstall torch
   pip install torch --index-url https://download.pytorch.org/whl/cu118
   ```

3. **Reduce max_new_tokens** in `medical_chatbot.py`:
   ```python
   max_new_tokens=256  # Instead of 512
   ```

### Issue 3: Import Errors

#### Symptom
```
ModuleNotFoundError: No module named 'transformers'
```

#### Solutions
1. **Verify virtual environment is activated**:
   ```bash
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

2. **Reinstall dependencies**:
   ```bash
   pip install -r requirements.txt --force-reinstall
   ```

3. **Check Python version**:
   ```bash
   python --version  # Should be 3.8+
   ```

### Issue 4: FAISS Installation Issues

#### Symptom
```
Error: Could not install faiss-cpu
```

#### Solutions
1. **For Windows**: Install Visual C++ Build Tools
   - Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

2. **For macOS**: Install with conda instead:
   ```bash
   conda install -c conda-forge faiss-cpu
   ```

3. **Alternative**: Use faiss-gpu if you have CUDA:
   ```bash
   pip install faiss-gpu
   ```

### Issue 5: Port Already in Use

#### Symptom
```
OSError: [Errno 48] Address already in use
```

#### Solutions
1. **Change port in app.py**:
   ```python
   app.run(debug=True, port=5001)  # Use different port
   ```

2. **Kill existing process**:
   ```bash
   # Windows
   netstat -ano | findstr :5000
   taskkill /PID <PID> /F
   
   # macOS/Linux
   lsof -ti:5000 | xargs kill -9
   ```

### Issue 6: Model Download Interrupted

#### Symptom
Download stops or fails midway

#### Solutions
1. **Clear cache and retry**:
   ```bash
   # Windows
   rmdir /s C:\Users\<username>\.cache\huggingface
   
   # macOS/Linux
   rm -rf ~/.cache/huggingface
   ```

2. **Download manually**:
   ```python
   from transformers import AutoModelForCausalLM
   model = AutoModelForCausalLM.from_pretrained(
       "BioMistral/BioMistral-7B",
       resume_download=True
   )
   ```

---

## ⚡ Performance Optimization

### For GPU Users
1. **Enable mixed precision**:
   ```python
   torch_dtype=torch.float16  # Already enabled in code
   ```

2. **Use flash attention** (if supported):
   ```bash
   pip install flash-attn
   ```

### For CPU Users
1. **Use quantized models**:
   ```python
   # In medical_chatbot.py
   load_in_8bit=True  # Reduces memory usage
   ```

2. **Limit concurrent requests**:
   - Use a queue system for multiple users

3. **Increase swap space** (Linux):
   ```bash
   sudo fallocate -l 8G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

### General Optimizations
1. **Preload model on startup** (already implemented)
2. **Cache embeddings** (already implemented in RAG)
3. **Use connection pooling** for database operations
4. **Enable gzip compression** for API responses

---

## 📊 Monitoring and Logging

### View Logs
Logs are printed to console. To save to file:
```bash
python app.py > app.log 2>&1
```

### Log Levels
- `INFO`: Normal operations
- `WARNING`: Non-critical issues (e.g., fallback model used)
- `ERROR`: Critical errors (e.g., model loading failed)

### Monitor Resource Usage
```bash
# CPU and Memory
htop  # Linux/macOS
# or
Task Manager  # Windows

# GPU Usage (NVIDIA)
nvidia-smi -l 1  # Updates every second
```

---

## 🔒 Security Considerations

1. **API Keys**: Store in environment variables, not in code
2. **HTTPS**: Use reverse proxy (nginx/Apache) for production
3. **Rate Limiting**: Implement to prevent abuse
4. **Input Validation**: Already implemented in safety validator
5. **CORS**: Configure appropriately for production

---

## 📚 Additional Resources

- **BioMistral Documentation**: https://huggingface.co/BioMistral/BioMistral-7B
- **Transformers Library**: https://huggingface.co/docs/transformers
- **FAISS Documentation**: https://github.com/facebookresearch/faiss
- **Flask Documentation**: https://flask.palletsprojects.com/

---

## 🆘 Getting Help

If you encounter issues not covered in this guide:

1. **Check test output**: Run `python test_chatbot.py` for diagnostics
2. **Review logs**: Look for ERROR messages in console output
3. **Check system resources**: Ensure sufficient RAM/disk space
4. **Verify dependencies**: Run `pip list` to check installed packages

---

## 📝 Notes

- **Model Updates**: BioMistral may release updated versions. Check HuggingFace for updates.
- **Cache Management**: Periodically clear cache if disk space is limited
- **Production Deployment**: Consider using Gunicorn/uWSGI instead of Flask dev server
- **Scaling**: For high traffic, consider model serving solutions like TorchServe or TensorFlow Serving

---

**Last Updated**: 2026-05-16  
**Version**: 1.0.0  
**Made with Bob** 🤖