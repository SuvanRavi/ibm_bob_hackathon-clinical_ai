"""
BioMedCLIP Training Script with LoRA Fine-tuning
Fine-tunes BioMedCLIP on HAM10000 dataset using LoRA adapters
"""

import os
import torch
import torch.nn as nn
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR
from transformers import AutoModel, AutoTokenizer, get_linear_schedule_with_warmup
from peft import LoraConfig, get_peft_model, TaskType
import open_clip
from tqdm import tqdm
import json
from datetime import datetime

from config import (
    MODEL_NAME, NUM_EPOCHS, LEARNING_RATE, LORA_R, LORA_ALPHA,
    LORA_DROPOUT, LORA_TARGET_MODULES, MODEL_CHECKPOINT_DIR,
    FINAL_MODEL_PATH, WARMUP_STEPS, WEIGHT_DECAY, GRADIENT_ACCUMULATION_STEPS,
    MAX_GRAD_NORM, SAVE_STEPS, EVAL_STEPS, LOGGING_STEPS, HAM10000_CLASSES
)
from dataset_loader import prepare_dataset


class BioMedCLIPClassifier(nn.Module):
    """BioMedCLIP with classification head"""
    
    def __init__(self, num_classes=7):
        super().__init__()
        
        # Load BioMedCLIP vision encoder
        print("Loading BioMedCLIP model...")
        self.model, _, self.preprocess = open_clip.create_model_and_transforms(
            'hf-hub:microsoft/BiomedCLIP-PubMedBERT_256-vit_base_patch16_224'
        )
        
        # Get embedding dimension
        self.embed_dim = self.model.visual.output_dim
        
        # Classification head
        self.classifier = nn.Sequential(
            nn.Linear(self.embed_dim, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, num_classes)
        )
        
    def forward(self, images):
        # Extract visual features
        features = self.model.encode_image(images)
        
        # Classify
        logits = self.classifier(features)
        return logits


def apply_lora(model):
    """Apply LoRA adapters to the model"""
    
    print("\n🔧 Applying LoRA adapters...")
    
    # Configure LoRA
    lora_config = LoraConfig(
        r=LORA_R,
        lora_alpha=LORA_ALPHA,
        target_modules=LORA_TARGET_MODULES,
        lora_dropout=LORA_DROPOUT,
        bias="none",
        task_type=TaskType.FEATURE_EXTRACTION
    )
    
    # Apply LoRA to vision encoder
    model.model.visual = get_peft_model(model.model.visual, lora_config)
    
    print(f"✓ LoRA applied with rank={LORA_R}, alpha={LORA_ALPHA}")
    print(f"✓ Target modules: {LORA_TARGET_MODULES}")
    
    # Print trainable parameters
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total_params = sum(p.numel() for p in model.parameters())
    print(f"✓ Trainable parameters: {trainable_params:,} / {total_params:,} ({100 * trainable_params / total_params:.2f}%)")
    
    return model


def train_epoch(model, train_loader, optimizer, scheduler, device, epoch):
    """Train for one epoch"""
    
    model.train()
    total_loss = 0
    correct = 0
    total = 0
    
    progress_bar = tqdm(train_loader, desc=f"Epoch {epoch+1}")
    
    for batch_idx, batch in enumerate(progress_bar):
        images = batch['image'].to(device)
        labels = batch['label'].to(device)
        
        # Forward pass
        logits = model(images)
        loss = nn.CrossEntropyLoss()(logits, labels)
        
        # Backward pass
        loss = loss / GRADIENT_ACCUMULATION_STEPS
        loss.backward()
        
        if (batch_idx + 1) % GRADIENT_ACCUMULATION_STEPS == 0:
            # Gradient clipping
            torch.nn.utils.clip_grad_norm_(model.parameters(), MAX_GRAD_NORM)
            
            # Update weights
            optimizer.step()
            scheduler.step()
            optimizer.zero_grad()
        
        # Calculate accuracy
        _, predicted = torch.max(logits, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()
        total_loss += loss.item() * GRADIENT_ACCUMULATION_STEPS
        
        # Update progress bar
        progress_bar.set_postfix({
            'loss': total_loss / (batch_idx + 1),
            'acc': 100 * correct / total,
            'lr': scheduler.get_last_lr()[0]
        })
    
    return total_loss / len(train_loader), 100 * correct / total


def validate(model, val_loader, device):
    """Validate the model"""
    
    model.eval()
    total_loss = 0
    correct = 0
    total = 0
    
    with torch.no_grad():
        for batch in tqdm(val_loader, desc="Validating"):
            images = batch['image'].to(device)
            labels = batch['label'].to(device)
            
            # Forward pass
            logits = model(images)
            loss = nn.CrossEntropyLoss()(logits, labels)
            
            # Calculate accuracy
            _, predicted = torch.max(logits, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            total_loss += loss.item()
    
    return total_loss / len(val_loader), 100 * correct / total


def save_checkpoint(model, optimizer, epoch, val_acc, checkpoint_dir):
    """Save model checkpoint"""
    
    os.makedirs(checkpoint_dir, exist_ok=True)
    
    checkpoint = {
        'epoch': epoch,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'val_acc': val_acc,
        'timestamp': datetime.now().isoformat()
    }
    
    checkpoint_path = os.path.join(checkpoint_dir, f'checkpoint_epoch_{epoch}.pt')
    torch.save(checkpoint, checkpoint_path)
    print(f"✓ Checkpoint saved: {checkpoint_path}")


def train():
    """Main training function"""
    
    print("\n" + "="*60)
    print("🚀 BioMedCLIP Training with LoRA")
    print("="*60)
    
    # Set device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"\n📱 Device: {device}")
    
    if device.type == 'cuda':
        print(f"   GPU: {torch.cuda.get_device_name(0)}")
        print(f"   Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
    
    # Prepare dataset
    train_loader, val_loader, test_loader, label_map = prepare_dataset()
    num_classes = len(label_map)
    
    # Initialize model
    print("\n🏗️ Building model...")
    model = BioMedCLIPClassifier(num_classes=num_classes)
    model = apply_lora(model)
    model = model.to(device)
    
    # Setup optimizer and scheduler
    optimizer = AdamW(
        model.parameters(),
        lr=LEARNING_RATE,
        weight_decay=WEIGHT_DECAY
    )
    
    total_steps = len(train_loader) * NUM_EPOCHS // GRADIENT_ACCUMULATION_STEPS
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=WARMUP_STEPS,
        num_training_steps=total_steps
    )
    
    print(f"\n📊 Training Configuration:")
    print(f"   Epochs: {NUM_EPOCHS}")
    print(f"   Batch size: {train_loader.batch_size}")
    print(f"   Learning rate: {LEARNING_RATE}")
    print(f"   Total steps: {total_steps}")
    print(f"   Warmup steps: {WARMUP_STEPS}")
    
    # Training loop
    print("\n🎯 Starting training...\n")
    
    best_val_acc = 0
    training_history = []
    
    for epoch in range(NUM_EPOCHS):
        print(f"\n{'='*60}")
        print(f"Epoch {epoch + 1}/{NUM_EPOCHS}")
        print(f"{'='*60}")
        
        # Train
        train_loss, train_acc = train_epoch(
            model, train_loader, optimizer, scheduler, device, epoch
        )
        
        # Validate
        val_loss, val_acc = validate(model, val_loader, device)
        
        # Log results
        print(f"\n📈 Results:")
        print(f"   Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}%")
        print(f"   Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.2f}%")
        
        # Save history
        training_history.append({
            'epoch': epoch + 1,
            'train_loss': train_loss,
            'train_acc': train_acc,
            'val_loss': val_loss,
            'val_acc': val_acc
        })
        
        # Save checkpoint if best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            print(f"\n🌟 New best validation accuracy: {val_acc:.2f}%")
            save_checkpoint(model, optimizer, epoch, val_acc, MODEL_CHECKPOINT_DIR)
            
            # Save as final model
            os.makedirs(os.path.dirname(FINAL_MODEL_PATH), exist_ok=True)
            torch.save({
                'model_state_dict': model.state_dict(),
                'label_map': label_map,
                'val_acc': val_acc,
                'epoch': epoch
            }, FINAL_MODEL_PATH + '.pt')
    
    # Save training history
    history_path = os.path.join(MODEL_CHECKPOINT_DIR, 'training_history.json')
    with open(history_path, 'w') as f:
        json.dump(training_history, f, indent=2)
    
    print("\n" + "="*60)
    print("✅ Training Complete!")
    print("="*60)
    print(f"Best validation accuracy: {best_val_acc:.2f}%")
    print(f"Model saved to: {FINAL_MODEL_PATH}.pt")
    print(f"Training history saved to: {history_path}")
    
    # Test on test set
    print("\n🧪 Evaluating on test set...")
    test_loss, test_acc = validate(model, test_loader, device)
    print(f"Test Loss: {test_loss:.4f} | Test Acc: {test_acc:.2f}%")
    
    return model, training_history


if __name__ == "__main__":
    try:
        model, history = train()
        print("\n🎉 Training completed successfully!")
    except KeyboardInterrupt:
        print("\n\n⚠️ Training interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Training failed with error: {e}")
        raise

# Made with Bob
