"""
Configuration file for BioMedCLIP model training and inference
"""

# Model Configuration
MODEL_NAME = "microsoft/BiomedCLIP-PubMedBERT_256-vit_base_patch16_224"
IMAGE_SIZE = 224
BATCH_SIZE = 16
NUM_EPOCHS = 10
LEARNING_RATE = 1e-4

# LoRA Configuration
LORA_R = 8  # Rank
LORA_ALPHA = 16  # Scaling factor
LORA_DROPOUT = 0.1
LORA_TARGET_MODULES = ["q_proj", "v_proj"]  # Attention layers to apply LoRA

# Dataset Configuration
DATASET_PATH = "data/ham10000"
TRAIN_SPLIT = 0.7
VAL_SPLIT = 0.15
TEST_SPLIT = 0.15

# HAM10000 Classes
HAM10000_CLASSES = {
    'akiec': 'Actinic keratoses and intraepithelial carcinoma',
    'bcc': 'Basal cell carcinoma',
    'bkl': 'Benign keratosis-like lesions',
    'df': 'Dermatofibroma',
    'mel': 'Melanoma',
    'nv': 'Melanocytic nevi',
    'vasc': 'Vascular lesions'
}

# Severity Mapping (based on medical severity)
SEVERITY_MAPPING = {
    'mel': {'level': 'severe', 'score': 9},  # Melanoma - most serious
    'bcc': {'level': 'severe', 'score': 8},  # Basal cell carcinoma
    'akiec': {'level': 'moderate', 'score': 7},  # Pre-cancerous
    'df': {'level': 'mild', 'score': 3},  # Benign
    'bkl': {'level': 'mild', 'score': 2},  # Benign
    'nv': {'level': 'mild', 'score': 1},  # Benign mole
    'vasc': {'level': 'moderate', 'score': 4}  # Vascular lesions
}

# Action Recommendations
ACTION_RECOMMENDATIONS = {
    'severe': "⚠️ URGENT: Schedule an appointment with a dermatologist or oncologist within 24-48 hours. This condition requires immediate medical evaluation.",
    'moderate': "⚡ IMPORTANT: Schedule an appointment with your physician within 1-2 weeks for proper evaluation and treatment planning.",
    'mild': "✓ MONITOR: This appears to be a benign condition. Monitor for any changes in size, shape, or color. Schedule a routine check-up if symptoms persist or worsen."
}

# Additional Notes by Condition
CONDITION_NOTES = {
    'mel': "Melanoma is a serious form of skin cancer. Early detection and treatment are crucial. Watch for changes in existing moles or new growths.",
    'bcc': "Basal cell carcinoma is the most common form of skin cancer. While rarely life-threatening, it requires prompt treatment to prevent local tissue damage.",
    'akiec': "Actinic keratoses are pre-cancerous lesions that can develop into squamous cell carcinoma. Regular monitoring and treatment are recommended.",
    'df': "Dermatofibroma is a benign skin growth. It's generally harmless but can be removed if it causes discomfort or cosmetic concerns.",
    'bkl': "Benign keratosis-like lesions are non-cancerous growths. They typically don't require treatment unless they cause irritation.",
    'nv': "Melanocytic nevi (moles) are usually benign. Monitor for any changes following the ABCDE rule: Asymmetry, Border, Color, Diameter, Evolution.",
    'vasc': "Vascular lesions are abnormalities of blood vessels in the skin. Most are benign but should be evaluated to rule out other conditions."
}

# Model Paths
MODEL_CHECKPOINT_DIR = "model/checkpoints"
FINAL_MODEL_PATH = "model/checkpoints/biomedclip_lora_final"

# Training Configuration
WARMUP_STEPS = 100
WEIGHT_DECAY = 0.01
GRADIENT_ACCUMULATION_STEPS = 2
MAX_GRAD_NORM = 1.0
SAVE_STEPS = 500
EVAL_STEPS = 500
LOGGING_STEPS = 100

# Inference Configuration
CONFIDENCE_THRESHOLD = 0.5  # Minimum confidence to return a prediction
TOP_K_PREDICTIONS = 3  # Number of top predictions to consider

# Made with Bob
