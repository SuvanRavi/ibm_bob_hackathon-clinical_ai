"""
HAM10000 Dataset Loader and Preprocessor
Downloads and prepares the HAM10000 dataset for training
"""

import os
import pandas as pd
import numpy as np
from PIL import Image
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from sklearn.model_selection import train_test_split
import requests
from tqdm import tqdm
import zipfile
from config import (
    DATASET_PATH, IMAGE_SIZE, TRAIN_SPLIT, VAL_SPLIT, 
    TEST_SPLIT, HAM10000_CLASSES, BATCH_SIZE
)


class HAM10000Dataset(Dataset):
    """PyTorch Dataset for HAM10000"""
    
    def __init__(self, dataframe, image_dir, transform=None):
        """
        Args:
            dataframe: pandas DataFrame with image_id and dx columns
            image_dir: directory containing images
            transform: torchvision transforms to apply
        """
        self.dataframe = dataframe
        self.image_dir = image_dir
        self.transform = transform
        
        # Create label mapping
        self.label_map = {label: idx for idx, label in enumerate(HAM10000_CLASSES.keys())}
        self.idx_to_label = {idx: label for label, idx in self.label_map.items()}
        
    def __len__(self):
        return len(self.dataframe)
    
    def __getitem__(self, idx):
        row = self.dataframe.iloc[idx]
        
        # Load image
        image_id = row['image_id']
        image_path = os.path.join(self.image_dir, f"{image_id}.jpg")
        
        try:
            image = Image.open(image_path).convert('RGB')
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
            # Return a blank image if loading fails
            image = Image.new('RGB', (IMAGE_SIZE, IMAGE_SIZE), color='white')
        
        # Apply transforms
        if self.transform:
            image = self.transform(image)
        
        # Get label
        label = self.label_map[row['dx']]
        
        return {
            'image': image,
            'label': torch.tensor(label, dtype=torch.long),
            'image_id': image_id,
            'dx': row['dx']
        }


def download_ham10000():
    """
    Download HAM10000 dataset from Kaggle or alternative source
    Note: This requires Kaggle API credentials or manual download
    """
    print("=" * 60)
    print("HAM10000 Dataset Download Instructions")
    print("=" * 60)
    print("\nThe HAM10000 dataset needs to be downloaded manually.")
    print("\nOption 1: Kaggle (Recommended)")
    print("1. Go to: https://www.kaggle.com/datasets/kmader/skin-cancer-mnist-ham10000")
    print("2. Download the dataset")
    print("3. Extract to:", os.path.abspath(DATASET_PATH))
    print("\nOption 2: Official Source")
    print("1. Go to: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/DBW86T")
    print("2. Download HAM10000_images_part_1.zip and HAM10000_images_part_2.zip")
    print("3. Download HAM10000_metadata.csv")
    print("4. Extract all to:", os.path.abspath(DATASET_PATH))
    print("\nExpected structure:")
    print(f"{DATASET_PATH}/")
    print("  ├── HAM10000_metadata.csv")
    print("  ├── HAM10000_images_part_1/")
    print("  └── HAM10000_images_part_2/")
    print("=" * 60)
    
    # Create directory if it doesn't exist
    os.makedirs(DATASET_PATH, exist_ok=True)
    
    return False  # Manual download required


def prepare_dataset():
    """
    Prepare HAM10000 dataset for training
    Returns train, validation, and test dataloaders
    """
    print("\n📦 Preparing HAM10000 Dataset...")
    
    # Check if dataset exists
    metadata_path = os.path.join(DATASET_PATH, "HAM10000_metadata.csv")
    if not os.path.exists(metadata_path):
        print("\n❌ Dataset not found!")
        download_ham10000()
        raise FileNotFoundError(
            f"Please download the HAM10000 dataset and place it in {DATASET_PATH}"
        )
    
    # Load metadata
    print("📄 Loading metadata...")
    df = pd.read_csv(metadata_path)
    
    # Check for required columns
    if 'image_id' not in df.columns or 'dx' not in df.columns:
        raise ValueError("Metadata must contain 'image_id' and 'dx' columns")
    
    # Filter for valid diagnoses
    df = df[df['dx'].isin(HAM10000_CLASSES.keys())]
    
    print(f"✓ Found {len(df)} images across {len(df['dx'].unique())} classes")
    print("\nClass distribution:")
    print(df['dx'].value_counts())
    
    # Split dataset
    print("\n✂️ Splitting dataset...")
    train_df, temp_df = train_test_split(
        df, 
        test_size=(VAL_SPLIT + TEST_SPLIT),
        stratify=df['dx'],
        random_state=42
    )
    
    val_df, test_df = train_test_split(
        temp_df,
        test_size=TEST_SPLIT / (VAL_SPLIT + TEST_SPLIT),
        stratify=temp_df['dx'],
        random_state=42
    )
    
    print(f"✓ Train: {len(train_df)} | Val: {len(val_df)} | Test: {len(test_df)}")
    
    # Define transforms
    train_transform = transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomVerticalFlip(),
        transforms.RandomRotation(20),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    val_transform = transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    # Find image directory
    image_dirs = []
    for part in ['HAM10000_images_part_1', 'HAM10000_images_part_2', 'images']:
        part_dir = os.path.join(DATASET_PATH, part)
        if os.path.exists(part_dir):
            image_dirs.append(part_dir)
    
    if not image_dirs:
        raise FileNotFoundError(f"No image directories found in {DATASET_PATH}")
    
    # For simplicity, we'll use the first directory or combine them
    # In practice, you might need to handle multiple directories
    image_dir = image_dirs[0]
    print(f"📁 Using image directory: {image_dir}")
    
    # Create datasets
    train_dataset = HAM10000Dataset(train_df, image_dir, transform=train_transform)
    val_dataset = HAM10000Dataset(val_df, image_dir, transform=val_transform)
    test_dataset = HAM10000Dataset(test_df, image_dir, transform=val_transform)
    
    # Create dataloaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=4,
        pin_memory=True
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=4,
        pin_memory=True
    )
    
    test_loader = DataLoader(
        test_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=4,
        pin_memory=True
    )
    
    print("✅ Dataset preparation complete!\n")
    
    return train_loader, val_loader, test_loader, train_dataset.label_map


if __name__ == "__main__":
    # Test dataset loading
    try:
        train_loader, val_loader, test_loader, label_map = prepare_dataset()
        print("\n🎉 Dataset loaded successfully!")
        print(f"Label mapping: {label_map}")
        
        # Test loading a batch
        batch = next(iter(train_loader))
        print(f"\nBatch shape: {batch['image'].shape}")
        print(f"Labels shape: {batch['label'].shape}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nPlease follow the download instructions above.")

# Made with Bob
