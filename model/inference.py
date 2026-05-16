"""
BioMedCLIP Inference Service
Loads trained model and performs inference on new images
"""

import os
import torch
import torch.nn as nn
from PIL import Image
import open_clip
from torchvision import transforms
import numpy as np
from datetime import datetime

from config import (
    IMAGE_SIZE, FINAL_MODEL_PATH, HAM10000_CLASSES,
    SEVERITY_MAPPING, ACTION_RECOMMENDATIONS, CONDITION_NOTES,
    CONFIDENCE_THRESHOLD, TOP_K_PREDICTIONS
)


class BioMedCLIPInference:
    """Inference service for BioMedCLIP model"""
    
    def __init__(self, model_path=None):
        """
        Initialize inference service
        
        Args:
            model_path: Path to trained model checkpoint
        """
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_path = model_path or (FINAL_MODEL_PATH + '.pt')
        
        # Label mapping
        self.label_map = {label: idx for idx, label in enumerate(HAM10000_CLASSES.keys())}
        self.idx_to_label = {idx: label for label, idx in self.label_map.items()}
        
        # Load model
        self.model = None
        self.load_model()
        
        # Define preprocessing transform
        self.transform = transforms.Compose([
            transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
    
    def load_model(self):
        """Load the trained model"""
        
        print(f"Loading model from {self.model_path}...")
        
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(
                f"Model not found at {self.model_path}. "
                "Please train the model first using train_biomedclip.py"
            )
        
        # Load checkpoint
        checkpoint = torch.load(self.model_path, map_location=self.device)
        
        # Recreate model architecture
        from train_biomedclip import BioMedCLIPClassifier
        self.model = BioMedCLIPClassifier(num_classes=len(self.label_map))
        
        # Load weights
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model = self.model.to(self.device)
        self.model.eval()
        
        print(f"✓ Model loaded successfully (Val Acc: {checkpoint.get('val_acc', 'N/A')}%)")
    
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
        
        # Apply transforms
        image_tensor = self.transform(image)
        
        # Add batch dimension
        image_tensor = image_tensor.unsqueeze(0)
        
        return image_tensor.to(self.device)
    
    def predict(self, image):
        """
        Perform inference on an image
        
        Args:
            image: PIL Image or path to image file
            
        Returns:
            Dictionary with predictions and probabilities
        """
        # Preprocess image
        image_tensor = self.preprocess_image(image)
        
        # Inference
        with torch.no_grad():
            logits = self.model(image_tensor)
            probabilities = torch.softmax(logits, dim=1)
        
        # Get top predictions
        top_probs, top_indices = torch.topk(probabilities, k=min(TOP_K_PREDICTIONS, len(self.label_map)))
        
        # Convert to numpy
        top_probs = top_probs.cpu().numpy()[0]
        top_indices = top_indices.cpu().numpy()[0]
        
        # Format predictions
        predictions = []
        for prob, idx in zip(top_probs, top_indices):
            label = self.idx_to_label[idx]
            predictions.append({
                'label': label,
                'condition': HAM10000_CLASSES[label],
                'confidence': float(prob)
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
                    for pred in predictions[1:] if pred['confidence'] > 0.1
                ]
            }
        }
        
        return analysis
    
    def batch_analyze(self, images):
        """
        Analyze multiple images
        
        Args:
            images: List of PIL Images or file paths
            
        Returns:
            List of analysis results
        """
        results = []
        for image in images:
            try:
                result = self.analyze_symptom(image)
                results.append(result)
            except Exception as e:
                results.append({
                    'success': False,
                    'error': str(e)
                })
        
        return results


# Global inference service instance (singleton pattern)
_inference_service = None


def get_inference_service():
    """Get or create inference service instance"""
    global _inference_service
    
    if _inference_service is None:
        _inference_service = BioMedCLIPInference()
    
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
        print("Usage: python inference.py <image_path>")
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
            print("📊 ANALYSIS RESULTS")
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
            
            print("\n" + "="*60)
        else:
            print(f"❌ Analysis failed: {result.get('message', result.get('error'))}")
    
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        raise

# Made with Bob
