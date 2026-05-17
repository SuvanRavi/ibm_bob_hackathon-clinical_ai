"""
BioMedCLIP Inference with Pre-trained Model (No Training Required)
Uses base BioMedCLIP for zero-shot classification
"""

import os
import torch
from PIL import Image
import open_clip
from torchvision import transforms
import numpy as np
from datetime import datetime

from config import (
    IMAGE_SIZE, HAM10000_CLASSES,
    SEVERITY_MAPPING, ACTION_RECOMMENDATIONS, CONDITION_NOTES,
    CONFIDENCE_THRESHOLD
)


class BioMedCLIPPretrainedInference:
    """Inference service using pre-trained BioMedCLIP (no fine-tuning needed)"""
    
    def __init__(self):
        """Initialize inference service with pre-trained model"""
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Using device: {self.device}")
        
        # Load pre-trained BioMedCLIP
        print("Loading pre-trained BioMedCLIP model...")
        self.model, _, self.preprocess = open_clip.create_model_and_transforms(
            'hf-hub:microsoft/BiomedCLIP-PubMedBERT_256-vit_base_patch16_224'
        )
        self.tokenizer = open_clip.get_tokenizer('hf-hub:microsoft/BiomedCLIP-PubMedBERT_256-vit_base_patch16_224')
        
        self.model = self.model.to(self.device)
        self.model.eval()
        
        # Create text prompts for each condition
        self.condition_texts = [
            f"A dermatoscopic image of {desc.lower()}"
            for desc in HAM10000_CLASSES.values()
        ]
        self.condition_labels = list(HAM10000_CLASSES.keys())
        
        # Encode text prompts
        with torch.no_grad():
            text_tokens = self.tokenizer(self.condition_texts).to(self.device)
            self.text_features = self.model.encode_text(text_tokens)
            self.text_features /= self.text_features.norm(dim=-1, keepdim=True)
        
        print("✓ Model loaded successfully (using pre-trained weights)")
    
    def preprocess_image(self, image):
        """
        Preprocess image for inference
        
        Args:
            image: PIL Image or path to image file
            
        Returns:
            Preprocessed tensor
        """
        # Load image if path is provided
        if isinstance(image, str):
            image = Image.open(image).convert('RGB')
        elif not isinstance(image, Image.Image):
            raise ValueError("Image must be a PIL Image or file path")
        
        # Apply preprocessing
        image_tensor = self.preprocess(image).unsqueeze(0).to(self.device)
        
        return image_tensor
    
    def predict(self, image):
        """
        Perform zero-shot classification on an image
        
        Args:
            image: PIL Image or path to image file
            
        Returns:
            Dictionary with predictions and probabilities
        """
        # Preprocess image
        image_tensor = self.preprocess_image(image)
        
        # Inference
        with torch.no_grad():
            image_features = self.model.encode_image(image_tensor)
            image_features /= image_features.norm(dim=-1, keepdim=True)
            
            # Calculate similarity scores
            similarity = (100.0 * image_features @ self.text_features.T).softmax(dim=-1)
        
        # Get predictions
        probs = similarity.cpu().numpy()[0]
        
        # Sort by probability
        sorted_indices = np.argsort(probs)[::-1]
        
        # Format predictions
        predictions = []
        for idx in sorted_indices[:3]:  # Top 3
            label = self.condition_labels[idx]
            predictions.append({
                'label': label,
                'condition': HAM10000_CLASSES[label],
                'confidence': float(probs[idx])
            })
        
        return predictions
    
    def analyze_symptom(self, image):
        """
        Analyze symptom and provide comprehensive assessment
        
        Args:
            image: PIL Image or path to image file
            
        Returns:
            Dictionary with complete analysis including severity and recommendations
        """
        # Get predictions
        predictions = self.predict(image)
        
        # Get top prediction
        top_prediction = predictions[0]
        label = top_prediction['label']
        confidence = top_prediction['confidence']
        
        # Check confidence threshold
        if confidence < CONFIDENCE_THRESHOLD:
            return {
                'success': False,
                'error': 'Low confidence prediction',
                'message': f'The model is not confident enough (confidence: {confidence:.2%}). Please provide a clearer image or consult a healthcare professional.',
                'confidence': confidence
            }
        
        # Get severity information
        severity_info = SEVERITY_MAPPING.get(label, {'level': 'moderate', 'score': 5})
        severity_level = severity_info['level']
        severity_score = severity_info['score']
        
        # Get recommendations
        recommended_action = ACTION_RECOMMENDATIONS.get(severity_level, ACTION_RECOMMENDATIONS['moderate'])
        additional_notes = CONDITION_NOTES.get(label, 'Please consult with a healthcare professional for proper diagnosis.')
        
        # Build comprehensive analysis
        analysis = {
            'success': True,
            'analysis': {
                'condition': top_prediction['condition'],
                'condition_code': label,
                'confidence': confidence,
                'severity': severity_level,
                'severity_score': severity_score,
                'recommended_action': recommended_action,
                'additional_notes': additional_notes,
                'timestamp': datetime.now().isoformat(),
                'alternative_diagnoses': [
                    {
                        'condition': pred['condition'],
                        'confidence': pred['confidence']
                    }
                    for pred in predictions[1:] if pred['confidence'] > 0.05
                ],
                'model_info': 'Using pre-trained BioMedCLIP (zero-shot classification)'
            }
        }
        
        return analysis


# Global inference service instance (singleton pattern)
_inference_service = None


def get_inference_service():
    """Get or create inference service instance"""
    global _inference_service
    
    if _inference_service is None:
        _inference_service = BioMedCLIPPretrainedInference()
    
    return _inference_service


def analyze_image(image):
    """
    Convenience function to analyze an image
    
    Args:
        image: PIL Image or path to image file
        
    Returns:
        Analysis result dictionary
    """
    service = get_inference_service()
    return service.analyze_symptom(image)


if __name__ == "__main__":
    # Test inference
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python inference_pretrained.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    if not os.path.exists(image_path):
        print(f"Error: Image not found at {image_path}")
        sys.exit(1)
    
    print(f"\n🔍 Analyzing image: {image_path}\n")
    
    try:
        result = analyze_image(image_path)
        
        if result['success']:
            analysis = result['analysis']
            print("="*60)
            print("📊 ANALYSIS RESULTS (Pre-trained Model)")
            print("="*60)
            print(f"\n🏥 Condition: {analysis['condition']}")
            print(f"📈 Confidence: {analysis['confidence']:.2%}")
            print(f"⚠️  Severity: {analysis['severity'].upper()} (Score: {analysis['severity_score']}/10)")
            print(f"\n💡 Recommended Action:")
            print(f"   {analysis['recommended_action']}")
            print(f"\n📝 Additional Notes:")
            print(f"   {analysis['additional_notes']}")
            
            if analysis['alternative_diagnoses']:
                print(f"\n🔄 Alternative Diagnoses:")
                for alt in analysis['alternative_diagnoses']:
                    print(f"   - {alt['condition']}: {alt['confidence']:.2%}")
            
            print(f"\nℹ️  {analysis['model_info']}")
            print("\n" + "="*60)
        else:
            print(f"❌ Analysis failed: {result.get('message', result.get('error'))}")
    
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        raise

# Made with Bob
