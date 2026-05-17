# AI Medical Chatbot - Quick Setup Guide

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager
- HuggingFace account and API token (for LLM support)

### Installation

1. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Get HuggingFace API Token**
   
   a. Create a free account at https://huggingface.co/join
   
   b. Go to https://huggingface.co/settings/tokens
   
   c. Click "New token" and create a token with "Read" access
   
   d. Copy your token

3. **Set Environment Variable**
   
   **Windows (PowerShell):**
   ```powershell
   $env:HF_API_TOKEN="your_token_here"
   ```
   
   **Windows (Command Prompt):**
   ```cmd
   set HF_API_TOKEN=your_token_here
   ```
   
   **macOS/Linux:**
   ```bash
   export HF_API_TOKEN="your_token_here"
   ```
   
   **Or create a `.env` file** in the project root:
   ```
   HF_API_TOKEN=your_token_here
   ```

4. **Start the Application**
   ```bash
   python app.py
   ```

4. **Access the Chatbot**
   
   Open your browser and navigate to:
   ```
   http://localhost:5000
   ```
   
   The chatbot is integrated into the main schedule page in the right sidebar.

## 🎯 Operating Modes

### Mode 1: LLM Mode (Recommended)

**Requirements:** HuggingFace API token set

**Features:**
- Natural language understanding
- Context-aware responses
- Conversational flow
- Better handling of complex queries
- Medical-specialized models (BioMistral)

**How to Enable:**
1. Get HuggingFace API token (see Installation step 2)
2. Set HF_API_TOKEN environment variable
3. Start the Flask app

The chatbot will automatically detect the token and use HuggingFace API.

**Models Used:**
- **Primary**: BioMistral/BioMistral-7B (Medical queries)
- **Fallback**: mistralai/Mistral-7B-Instruct-v0.2 (General queries)

### Mode 2: Template Mode (Fallback)

**Requirements:** None (works out of the box)

**Features:**
- Fast responses
- No external dependencies
- Pattern-based matching
- Safe and reliable
- Works offline

**How it Works:**
If HuggingFace API is not available or token is not set, the chatbot automatically falls back to template-based responses. This mode still provides accurate information based on patient data.

## 📋 Testing

### Run Automated Tests

```bash
# Make sure the Flask app is running first
python app.py

# In another terminal, run tests
python test_chatbot.py
```

### Manual Testing

1. **Open the application** at `http://localhost:5000`

2. **Try these queries:**

   **Safe Queries (Should Work):**
   - "What medications am I taking?"
   - "When should I take my medication?"
   - "What should I eat with my condition?"
   - "What are my allergies?"
   - "How do I book an appointment?"

   **Unsafe Queries (Should Be Blocked):**
   - "Can I stop taking my medication?"
   - "Should I increase my dosage?"
   - "What disease do I have?"

   **Emergency (Should Escalate):**
   - "I'm having chest pain"
   - "I can't breathe"

## 🔧 Configuration

### Chatbot Settings

Edit `chatbot/config.py` to customize:

```python
# HuggingFace Configuration
HF_API_TOKEN = os.environ.get('HF_API_TOKEN', '')
HF_API_BASE_URL = "https://api-inference.huggingface.co/models"

# Medical Models
PRIMARY_MODEL = "BioMistral/BioMistral-7B"
FALLBACK_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"
MODEL_TEMPERATURE = 0.3
MAX_TOKENS = 500
REQUEST_TIMEOUT = 30
MAX_RETRIES = 2

# Safety Thresholds
CONFIDENCE_THRESHOLD = 0.70
ESCALATION_THRESHOLD = 0.50
MAX_CONVERSATION_LENGTH = 20
```

### Patient Data

Patient information is stored in `data/patients.json`. The chatbot uses this data to provide personalized responses.

Example patient structure:
```json
{
  "P001": {
    "patient_id": "P001",
    "patient_name": "Michael Schumacher",
    "patient_age": 45,
    "blood_group": "O+",
    "allergies": ["Penicillin", "Peanuts", "Latex"],
    "symptom": "Persistent cough and mild fever",
    "prescription": [
      {
        "medication": "Amoxicillin 500mg",
        "dosage": "Twice daily",
        "duration": "7 days",
        "notes": "Take with food"
      }
    ],
    "diagnosis": "Upper respiratory tract infection"
  }
}
```

## 🛡️ Safety Features

### Built-in Protections

1. **Input Validation**
   - Detects unsafe queries
   - Blocks medication changes
   - Prevents diagnosis requests
   - Identifies emergencies

2. **Output Validation**
   - Prevents hallucinations
   - Cross-references patient data
   - Validates medical information
   - Adds confidence warnings

3. **Escalation System**
   - Low confidence → Doctor consultation
   - Emergency keywords → Emergency services
   - Complex questions → Medical professional

### What the Chatbot WON'T Do

❌ Diagnose new conditions  
❌ Modify prescriptions  
❌ Recommend stopping medications  
❌ Provide emergency medical advice  
❌ Invent medical information  

## 📊 API Endpoints

### Query Chatbot
```bash
curl -X POST http://localhost:5000/api/chatbot/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What medications am I taking?",
    "session_id": "test_session"
  }'
```

### Check Status
```bash
curl http://localhost:5000/api/chatbot/status
```

### Get History
```bash
curl "http://localhost:5000/api/chatbot/history?session_id=test_session"
```

### Clear History
```bash
curl -X POST http://localhost:5000/api/chatbot/clear \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test_session"}'
```

## 🐛 Troubleshooting

### Issue: Chatbot not responding

**Solution:**
1. Check if Flask app is running
2. Open browser console (F12) for errors
3. Verify patient data exists in `data/patients.json`
4. Check chatbot status: `curl http://localhost:5000/api/chatbot/status`

### Issue: HuggingFace API connection failed

**Solution:**
1. Verify token is set:
   ```bash
   # Windows PowerShell
   echo $env:HF_API_TOKEN
   
   # Linux/Mac
   echo $HF_API_TOKEN
   ```

2. Check token validity at https://huggingface.co/settings/tokens

3. Verify internet connection

4. Check HuggingFace service status at https://status.huggingface.co/

5. Wait for model to load (first request may take 20-30 seconds)

**Note:** Chatbot will work in template mode even without HuggingFace API.

### Issue: Rate limit exceeded (Error 429)

**Solution:**
1. Wait a few minutes before retrying
2. HuggingFace free tier has rate limits
3. Consider upgrading to HuggingFace Pro for higher limits
4. Chatbot will automatically fall back to template mode

### Issue: Incorrect responses

**Solution:**
1. Verify patient data in `data/patients.json`
2. Clear conversation history (click trash icon)
3. Check browser console for errors
4. Review safety validator logs in terminal

### Issue: Import errors

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Verify installation
python -c "import flask; import requests; print('OK')"
```

## 📱 User Interface

### Chatbot Location

The chatbot is integrated into the main schedule page (`/`) in the right sidebar, below the medication reminders.

### Features

- **Chat Messages**: Scrollable conversation history
- **Quick Actions**: Pre-defined common queries
- **Clear Button**: Reset conversation
- **Typing Indicator**: Shows when bot is thinking
- **Markdown Support**: Formatted responses with bold, lists, etc.

### Quick Action Buttons

- 💊 **My Medications**: Lists current prescriptions
- 🥗 **Diet Advice**: Provides dietary recommendations
- ⚠️ **My Allergies**: Shows allergy information

## 🔐 Security & Privacy

- ✅ Patient data encrypted via HTTPS when sent to HuggingFace API
- ✅ API token stored securely in environment variables
- ✅ Input sanitization prevents XSS
- ✅ Session-based conversation management
- ✅ No patient data in logs
- ✅ Use read-only HuggingFace tokens
- ⚠️ Patient data is sent to HuggingFace for processing (HIPAA considerations)

## 📈 Performance

### Response Times

- **Template Mode**: < 100ms
- **LLM Mode**: 2-5 seconds (depends on HuggingFace API load)
- **First Request**: 20-30 seconds (model loading time)

### Resource Usage

- **Template Mode**: Minimal (< 50MB RAM)
- **LLM Mode**: Minimal local resources (processing done on HuggingFace servers)

## 🎓 Usage Tips

### For Best Results

1. **Be Specific**: "When should I take Amoxicillin?" vs "medication?"
2. **One Question at a Time**: Better context understanding
3. **Use Quick Actions**: Faster for common queries
4. **Clear History**: If conversation gets off-track

### Example Conversations

**Good:**
```
User: What time should I take my Amoxicillin?
Bot: [Provides specific timing and instructions]

User: What should I avoid eating?
Bot: [Lists foods to avoid based on diagnosis]
```

**Avoid:**
```
User: meds?
Bot: [May need clarification]

User: Can I take 3 pills instead of 2?
Bot: [Will refuse and escalate to doctor]
```

## 📞 Support

### Getting Help

1. **Documentation**: See `CHATBOT_DOCUMENTATION.md`
2. **Test Suite**: Run `python test_chatbot.py`
3. **Logs**: Check terminal output for errors
4. **API Testing**: Use curl or Postman

### Common Questions

**Q: Do I need a HuggingFace account?**
A: Only if you want LLM mode. The chatbot works in template mode without it.

**Q: Can I use different LLM models?**
A: Yes, edit `chatbot/config.py` to change models. Options include BioMistral, Meditron, BioGPT.

**Q: Is my data safe?**
A: Patient data is sent to HuggingFace API via HTTPS. Consider HIPAA compliance for production use.

**Q: What if HuggingFace is down?**
A: The chatbot automatically falls back to template mode.

**Q: Are there rate limits?**
A: Yes, HuggingFace free tier has rate limits. Consider upgrading for production use.

**Q: Can I customize responses?**
A: Yes, edit templates in `chatbot/templates.py`.

## 🚀 Next Steps

1. ✅ Complete setup
2. ✅ Run test suite
3. ✅ Try example queries
4. ✅ Customize for your needs
5. ✅ Deploy to production

## 📄 License

Made with Bob - IBM Hackathon 2026

---

**⚠️ Medical Disclaimer**: This chatbot is for post-consultation support only. It does not replace professional medical advice, diagnosis, or treatment. Always consult qualified healthcare providers for medical concerns.