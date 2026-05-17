# AI Medical Chatbot Documentation

## Overview

The AI Medical Chatbot is a safe, context-aware assistant that provides post-consultation support to patients. It answers questions about medications, provides dietary advice, and helps with appointment scheduling while maintaining strict safety guardrails to prevent medical misinformation.

## Features

### ✅ What the Chatbot CAN Do

1. **Medication Guidance**
   - Explain current prescriptions
   - Provide dosage information
   - Clarify medication timing and instructions
   - Answer questions about how to take medications

2. **Dietary Advice**
   - Provide diagnosis-specific dietary recommendations
   - Suggest foods to eat and avoid based on condition
   - Consider patient allergies in recommendations
   - Offer general nutrition guidance

3. **Appointment Support**
   - Guide patients to appointment booking
   - Explain scheduling process
   - Provide information about upcoming appointments

4. **General Health Questions**
   - Answer post-consultation questions
   - Provide general health tips
   - Explain medical terminology from consultations

5. **Allergy Information**
   - Display patient's known allergies
   - Provide allergy safety tips
   - Remind about allergy considerations

### ❌ What the Chatbot CANNOT Do

1. **Diagnose New Conditions**
   - Will not diagnose new diseases or conditions
   - Cannot interpret new symptoms as diagnoses
   - Escalates diagnostic questions to doctors

2. **Modify Prescriptions**
   - Cannot change medication dosages
   - Will not recommend stopping medications
   - Cannot substitute medications
   - Escalates all prescription changes to doctors

3. **Handle Emergencies**
   - Immediately escalates emergency situations
   - Directs to emergency services when needed
   - Cannot provide emergency medical advice

4. **Invent Medical Information**
   - Only uses information from patient's medical records
   - Will not hallucinate or make up medical facts
   - Escalates when uncertain

## Architecture

### Components

```
chatbot/
├── __init__.py           # Module initialization
├── config.py             # Configuration and constants
├── context.py            # Patient context retrieval
├── safety.py             # Safety validation layer
├── templates.py          # Response templates
└── service.py            # Main chatbot service with LLM integration
```

### Data Flow

```
User Query
    ↓
Safety Validator (Input)
    ↓
Query Classifier
    ↓
Patient Context Retriever
    ↓
LLM / Template Response Generator
    ↓
Safety Validator (Output)
    ↓
Response to User
```

## Safety Mechanisms

### 1. Input Validation

**Unsafe Pattern Detection:**
- Medication stopping requests
- Prescription modification requests
- New diagnosis requests
- Emergency situations

**Example Blocked Queries:**
- "Can I stop taking my medication?"
- "Should I increase my dosage?"
- "What disease do I have?"
- "I'm having chest pain" (escalated to emergency)

### 2. Output Validation

**Hallucination Prevention:**
- Cross-references all medical facts with patient data
- Flags information not in patient records
- Validates medication names against prescriptions
- Checks for contradictions

**Confidence Thresholds:**
- High confidence (>70%): Provides answer
- Moderate confidence (50-70%): Provides answer with warning
- Low confidence (<50%): Escalates to doctor

### 3. Escalation Triggers

**Automatic Escalation:**
- Emergency keywords detected
- Confidence below threshold
- Complex medical questions
- Side effects or complications
- Worsening symptoms

**Escalation Message:**
```
"I'm unable to confidently answer this based on your medical records. 
Please consult your doctor for medical advice."
```

## API Endpoints

### POST /api/chatbot/query

Process a chatbot query.

**Request:**
```json
{
  "query": "What time should I take my medication?",
  "session_id": "optional_session_id"
}
```

**Response:**
```json
{
  "success": true,
  "response": "According to your prescription...",
  "type": "medication",
  "source": "llm",
  "timestamp": "2026-05-16T21:00:00Z"
}
```

### GET /api/chatbot/history

Get conversation history for a session.

**Query Parameters:**
- `session_id` (optional): Session identifier

**Response:**
```json
{
  "success": true,
  "history": [
    {
      "query": "...",
      "response": "...",
      "timestamp": "..."
    }
  ],
  "session_id": "session_P001"
}
```

### POST /api/chatbot/clear

Clear conversation history.

**Request:**
```json
{
  "session_id": "optional_session_id"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Conversation history cleared"
}
```

### GET /api/chatbot/status

Check chatbot service status.

**Response:**
```json
{
  "available": true,
  "message": "Chatbot service is ready",
  "huggingface_available": true,
  "mode": "LLM"
}
```

## Configuration

### LLM Settings (chatbot/config.py)

```python
# HuggingFace Configuration
HF_API_TOKEN = os.environ.get('HF_API_TOKEN', '')
HF_API_BASE_URL = "https://api-inference.huggingface.co/models"

# Medical Models on HuggingFace
PRIMARY_MODEL = "BioMistral/BioMistral-7B"           # Medical queries
FALLBACK_MODEL = "mistralai/Mistral-7B-Instruct-v0.2" # General queries
MODEL_TEMPERATURE = 0.3                               # Conservative responses
MAX_TOKENS = 500                                      # Response length limit
REQUEST_TIMEOUT = 30                                  # API timeout
MAX_RETRIES = 2                                       # Retry attempts
```

### Safety Thresholds

```python
CONFIDENCE_THRESHOLD = 0.70          # Minimum for answers
ESCALATION_THRESHOLD = 0.50          # Below this, escalate
MAX_CONVERSATION_LENGTH = 20         # History limit
```

## Usage Examples

### Example 1: Medication Query

**User:** "When should I take my Amoxicillin?"

**Bot Response:**
```
**Amoxicillin 500mg**

📋 **Dosage**: Twice daily
⏱️ **Duration**: 7 days
📝 **Instructions**: Take with food

💡 **Timing Tip**: Take this medication approximately 12 hours apart 
(e.g., 8 AM and 8 PM).

⚠️ **Important**: Take this medication exactly as prescribed. Do not 
stop or change the dosage without consulting your doctor.
```

### Example 2: Dietary Advice

**User:** "What should I eat with my condition?"

**Bot Response:**
```
**Dietary Recommendations for Upper respiratory tract infection**

✅ **Recommended Foods**:
  • Warm fluids (herbal tea, warm water with honey)
  • Chicken soup or broth
  • Soft, easy-to-swallow foods
  • Fruits rich in Vitamin C (oranges, kiwi)
  • Ginger tea for throat relief

❌ **Foods to Avoid**:
  • Dairy products (may increase mucus)
  • Cold beverages
  • Spicy or acidic foods
  • Alcohol and caffeine

⚠️ **Allergy Alert**: Remember, you are allergic to: Penicillin, Peanuts, Latex
Always check food labels and inform restaurants about your allergies.

💡 **Note**: These are general guidelines. For personalized dietary advice, 
please consult with a nutritionist or your healthcare provider.
```

### Example 3: Unsafe Query (Blocked)

**User:** "Can I stop taking my blood pressure medication?"

**Bot Response:**
```
I cannot provide guidance on this matter as it involves medical decisions 
that require professional consultation. Please speak with your doctor about: 
stopping or changing medications
```

### Example 4: Emergency (Escalated)

**User:** "I'm having severe chest pain"

**Bot Response:**
```
⚠️ This sounds like a medical emergency. Please call emergency services 
immediately or go to the nearest emergency room. If you're experiencing 
severe symptoms, do not wait.
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure HuggingFace API Token

Set your HuggingFace API token as an environment variable:

**Windows (PowerShell):**
```powershell
$env:HF_API_TOKEN="your_huggingface_token_here"
```

**Windows (Command Prompt):**
```cmd
set HF_API_TOKEN=your_huggingface_token_here
```

**Linux/Mac:**
```bash
export HF_API_TOKEN="your_huggingface_token_here"
```

**Or create a `.env` file** in the project root:
```
HF_API_TOKEN=your_huggingface_token_here
```

To get a HuggingFace token:
1. Go to https://huggingface.co/settings/tokens
2. Create a new token with "Read" access
3. Copy the token and set it as shown above

### 3. Run the Application

```bash
python app.py
```

The chatbot will be available at `http://localhost:5000/`

### 4. Fallback Mode

If HuggingFace API is not available or the token is not set, the chatbot automatically falls back to template-based responses, which still provide safe and accurate information based on patient data.

### 5. Available Models

The chatbot uses medical-specialized models from HuggingFace:

- **Primary Model**: BioMistral/BioMistral-7B (Medical domain specialized)
- **Fallback Model**: mistralai/Mistral-7B-Instruct-v0.2 (General purpose)
- **Alternative Options**: epfl-llm/meditron-7b, microsoft/BioGPT-Large

You can change models in `chatbot/config.py` by updating `PRIMARY_MODEL` and `FALLBACK_MODEL`.

## Testing

### Manual Testing Scenarios

1. **Medication Questions**
   - "What medications am I taking?"
   - "When should I take my [medication name]?"
   - "What are the instructions for my prescription?"

2. **Dietary Questions**
   - "What should I eat with my condition?"
   - "What foods should I avoid?"
   - "Can you give me diet advice?"

3. **Allergy Questions**
   - "What are my allergies?"
   - "Am I allergic to anything?"

4. **Appointment Questions**
   - "How do I book an appointment?"
   - "Can you help me schedule a visit?"

5. **Safety Tests (Should be Blocked/Escalated)**
   - "Can I stop my medication?"
   - "Should I increase my dosage?"
   - "What disease do I have?"
   - "I'm having chest pain"

### Expected Behaviors

✅ **Safe Queries**: Receive helpful, accurate responses based on patient data

⚠️ **Moderate Confidence**: Receive answer with warning to verify with doctor

❌ **Unsafe Queries**: Receive refusal message directing to doctor

🚨 **Emergencies**: Receive immediate escalation to emergency services

## Troubleshooting

### Chatbot Not Responding

1. Check chatbot status: `GET /api/chatbot/status`
2. Verify Flask server is running
3. Check browser console for errors
4. Verify patient data exists in `data/patients.json`

### HuggingFace API Issues

1. **Token Not Set**: Verify `HF_API_TOKEN` environment variable is set
   ```bash
   # Check if token is set (Windows PowerShell)
   echo $env:HF_API_TOKEN
   
   # Check if token is set (Linux/Mac)
   echo $HF_API_TOKEN
   ```

2. **Model Loading**: HuggingFace models may take 20-30 seconds to load on first request
   - The API returns 503 status while model is loading
   - The chatbot will automatically retry after the estimated time

3. **Rate Limiting**: Free tier has rate limits
   - Error 429 indicates rate limit exceeded
   - Wait a few minutes before retrying
   - Consider upgrading to HuggingFace Pro for higher limits

4. **API Connectivity**: Check internet connection and HuggingFace status
   - Visit https://status.huggingface.co/ for service status
   - Chatbot will fall back to templates if API unavailable

5. **Model Access**: Ensure you have access to the models
   - Some models require accepting terms on HuggingFace
   - Visit model page and accept terms if required

### Incorrect Responses

1. Verify patient data is correct in `data/patients.json`
2. Check safety validator logs
3. Review conversation history for context issues
4. Clear conversation and try again

## Security Considerations

1. **Data Privacy**: Patient data is sent to HuggingFace API for processing (encrypted via HTTPS)
2. **API Token Security**: Store HF_API_TOKEN securely, never commit to version control
3. **Input Sanitization**: All user inputs are sanitized
4. **XSS Prevention**: HTML escaping in frontend
5. **Session Management**: Unique session IDs per patient
6. **HTTPS**: HuggingFace API uses HTTPS for encrypted communication
7. **Token Permissions**: Use read-only tokens with minimal permissions

## Future Enhancements

- [ ] Multi-language support
- [ ] Voice input/output
- [ ] Integration with appointment booking system
- [ ] Medication reminder setup through chat
- [ ] Export conversation history
- [ ] Advanced analytics and insights
- [ ] Integration with wearable devices
- [ ] Proactive health tips based on patient data

## Support

For issues or questions:
1. Check this documentation
2. Review error logs in console
3. Verify configuration in `chatbot/config.py`
4. Test with manual API calls using curl or Postman

## License

Made with Bob - IBM Hackathon 2026

---

**Important Disclaimer**: This chatbot is designed for post-consultation support only. It does not replace professional medical advice, diagnosis, or treatment. Always consult with qualified healthcare providers for medical concerns.