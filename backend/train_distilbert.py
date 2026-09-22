"""
CyberShield — DistilBERT Phishing Classifier Training & ONNX Export
===================================================================
Fine-tunes distilbert-base-uncased for binary phishing/safe text classification,
then exports to ONNX format with INT8 quantization for Snapdragon NPU deployment.

Usage:
    python train_distilbert.py

Outputs:
    models/distilbert_phishing.onnx         (FP32 ONNX model)
    models/distilbert_phishing_int8.onnx    (INT8 quantized for NPU)
    models/tokenizer/                       (saved tokenizer)
"""
import os
import sys
import json
import numpy as np
import pandas as pd

# ─── Configuration ────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")
DATA_DIR = os.path.join(BASE_DIR, "data")
TOKENIZER_DIR = os.path.join(MODEL_DIR, "tokenizer")
ONNX_OUTPUT = os.path.join(MODEL_DIR, "distilbert_phishing.onnx")
ONNX_QUANTIZED = os.path.join(MODEL_DIR, "distilbert_phishing_int8.onnx")

MAX_LENGTH = 128
BATCH_SIZE = 16
EPOCHS = 3
LEARNING_RATE = 2e-5


def load_dataset():
    """Load the phishing dataset from the data/ directory."""
    csv_path = os.path.join(DATA_DIR, "phishing_dataset.csv")
    if not os.path.exists(csv_path):
        print(f"Dataset not found at {csv_path}")
        print("Generating dataset from train_model.py...")
        # Import the dataset creator from existing training script
        sys.path.insert(0, BASE_DIR)
        from train_model import create_dataset
        create_dataset()
    
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} samples from dataset")
    print(f"Label distribution:\n{df['label'].value_counts()}")
    return df


def train_and_export():
    """Fine-tune DistilBERT and export to ONNX."""
    import torch
    from torch.utils.data import DataLoader, Dataset
    from torch.optim import AdamW
    from transformers import (
        AutoTokenizer,
        AutoModelForSequenceClassification,
        get_linear_schedule_with_warmup
    )
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, f1_score, classification_report
    
    # Load data
    df = load_dataset()
    texts = df["text"].tolist()
    labels = df["label"].tolist()  # 0=safe, 1=phishing
    
    # Split
    train_texts, val_texts, train_labels, val_labels = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )
    print(f"Train: {len(train_texts)}, Validation: {len(val_texts)}")
    
    # Tokenizer
    print("Loading DistilBERT tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
    
    # Save tokenizer for inference
    os.makedirs(TOKENIZER_DIR, exist_ok=True)
    tokenizer.save_pretrained(TOKENIZER_DIR)
    print(f"Tokenizer saved to {TOKENIZER_DIR}")
    
    # Custom Dataset
    class PhishingDataset(Dataset):
        def __init__(self, texts, labels, tokenizer, max_length):
            self.encodings = tokenizer(
                texts, padding="max_length", truncation=True,
                max_length=max_length, return_tensors="pt"
            )
            self.labels = torch.tensor(labels, dtype=torch.long)
        
        def __len__(self):
            return len(self.labels)
        
        def __getitem__(self, idx):
            return {
                "input_ids": self.encodings["input_ids"][idx],
                "attention_mask": self.encodings["attention_mask"][idx],
                "labels": self.labels[idx]
            }
    
    train_dataset = PhishingDataset(train_texts, train_labels, tokenizer, MAX_LENGTH)
    val_dataset = PhishingDataset(val_texts, val_labels, tokenizer, MAX_LENGTH)
    
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE)
    
    # Model
    print("Loading DistilBERT model for sequence classification...")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = AutoModelForSequenceClassification.from_pretrained(
        "distilbert-base-uncased", num_labels=2
    ).to(device)
    
    # Optimizer & Scheduler
    optimizer = AdamW(model.parameters(), lr=LEARNING_RATE, weight_decay=0.01)
    total_steps = len(train_loader) * EPOCHS
    scheduler = get_linear_schedule_with_warmup(
        optimizer, num_warmup_steps=total_steps // 10, num_training_steps=total_steps
    )
    
    # Training loop
    print(f"\nTraining on {device} for {EPOCHS} epochs...")
    best_f1 = 0.0
    
    for epoch in range(EPOCHS):
        model.train()
        total_loss = 0
        
        for batch_idx, batch in enumerate(train_loader):
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)
            
            outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
            loss = outputs.loss
            total_loss += loss.item()
            
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            scheduler.step()
            optimizer.zero_grad()
            
            if (batch_idx + 1) % 10 == 0:
                print(f"  Epoch {epoch+1}/{EPOCHS}, Batch {batch_idx+1}/{len(train_loader)}, Loss: {loss.item():.4f}")
        
        avg_loss = total_loss / len(train_loader)
        
        # Validation
        model.eval()
        all_preds = []
        all_labels = []
        
        with torch.no_grad():
            for batch in val_loader:
                input_ids = batch["input_ids"].to(device)
                attention_mask = batch["attention_mask"].to(device)
                labels = batch["labels"].to(device)
                
                outputs = model(input_ids=input_ids, attention_mask=attention_mask)
                preds = torch.argmax(outputs.logits, dim=1)
                all_preds.extend(preds.cpu().numpy())
                all_labels.extend(labels.cpu().numpy())
        
        acc = accuracy_score(all_labels, all_preds)
        f1 = f1_score(all_labels, all_preds, average="binary")
        print(f"  Epoch {epoch+1}: Loss={avg_loss:.4f}, Accuracy={acc:.4f}, F1={f1:.4f}")
        
        if f1 > best_f1:
            best_f1 = f1
            # Save best model weights for ONNX export
            torch.save(model.state_dict(), os.path.join(MODEL_DIR, "distilbert_best.pt"))
    
    print(f"\nBest Validation F1: {best_f1:.4f}")
    print(classification_report(all_labels, all_preds, target_names=["Safe", "Phishing"]))
    
    # ─── ONNX Export ──────────────────────────────────────────────
    print("\nExporting model to ONNX format...")
    model.eval()
    model.to("cpu")
    
    # Create dummy inputs
    dummy_input_ids = torch.ones(1, MAX_LENGTH, dtype=torch.long)
    dummy_attention_mask = torch.ones(1, MAX_LENGTH, dtype=torch.long)
    
    torch.onnx.export(
        model,
        (dummy_input_ids, dummy_attention_mask),
        ONNX_OUTPUT,
        export_params=True,
        opset_version=18,
        do_constant_folding=True,
        input_names=["input_ids", "attention_mask"],
        output_names=["logits"],
        dynamic_axes={
            "input_ids": {0: "batch_size"},
            "attention_mask": {0: "batch_size"},
            "logits": {0: "batch_size"}
        }
    )
    
    onnx_size = os.path.getsize(ONNX_OUTPUT) / (1024 * 1024)
    print(f"ONNX model saved to {ONNX_OUTPUT} ({onnx_size:.1f} MB)")
    
    # ─── INT8 Quantization ────────────────────────────────────────
    print("\nApplying INT8 dynamic quantization...")
    try:
        from onnxruntime.quantization import quantize_dynamic, QuantType
        
        quantize_dynamic(
            ONNX_OUTPUT,
            ONNX_QUANTIZED,
            weight_type=QuantType.QInt8
        )
        
        q_size = os.path.getsize(ONNX_QUANTIZED) / (1024 * 1024)
        print(f"Quantized model saved to {ONNX_QUANTIZED} ({q_size:.1f} MB)")
        print(f"Size reduction: {onnx_size:.1f} MB -> {q_size:.1f} MB ({(1 - q_size/onnx_size)*100:.0f}% smaller)")
    except Exception as e:
        print(f"Quantization failed (non-critical): {e}")
        print("The FP32 ONNX model will still work with CPU execution provider.")
    
    # ─── Verify ONNX Model ────────────────────────────────────────
    print("\nVerifying ONNX model...")
    import onnxruntime as ort
    
    test_model_path = ONNX_QUANTIZED if os.path.exists(ONNX_QUANTIZED) else ONNX_OUTPUT
    session = ort.InferenceSession(test_model_path, providers=["CPUExecutionProvider"])
    
    # Test inference
    test_text = "URGENT: Your account has been compromised. Click here to verify."
    encoded = tokenizer(test_text, padding="max_length", truncation=True, max_length=MAX_LENGTH, return_tensors="np")
    
    outputs = session.run(None, {
        "input_ids": encoded["input_ids"].astype(np.int64),
        "attention_mask": encoded["attention_mask"].astype(np.int64)
    })
    
    logits = outputs[0][0]
    probs = np.exp(logits) / np.exp(logits).sum()
    print(f"Test input: '{test_text[:50]}...'")
    print(f"Prediction: Safe={probs[0]:.4f}, Phishing={probs[1]:.4f}")
    print("\nONNX export and verification complete!")


if __name__ == "__main__":
    os.makedirs(MODEL_DIR, exist_ok=True)
    train_and_export()
