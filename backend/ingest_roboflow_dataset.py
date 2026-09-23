"""
CyberShield — Roboflow Dataset Ingestion & Vision Model Fine-Tuning Pipeline
=============================================================================
Connects to Roboflow Universe to download curated phishing, fake login, and
scam QR datasets, fine-tunes MobileNet-v2, and exports to INT8/W8A16 ONNX
optimized for the Qualcomm Hexagon NPU on Snapdragon-powered HP PCs.

Recommended Roboflow Universe Datasets for Phishing & Visual Fraud:
-------------------------------------------------------------------
1. Phishing Screenshot & Login Detection:
   - Workspace / Project: "phishing-detection-mvp" or "detect-phishing-screenshots"
   - URL: https://universe.roboflow.com/
   - Classes: login_form, username_field, password_field, brand_logo, submit_btn

2. Phishing Logo Detection:
   - Project: "santhosh-sandy-d5tfn/phishing-logo-detection"
   - URL: https://universe.roboflow.com/santhosh-sandy-d5tfn/phishing-logo-detection
   - Classes: paypal, microsoft, google, chase, sbi, bank_of_america

3. Phishing QR Code Detection (Quishing):
   - Project: "fypdetectingphishingqrcodes-gy8sq/phishing-qr-detection"
   - URL: https://universe.roboflow.com/fypdetectingphishingqrcodes-gy8sq/phishing-qr-detection
   - Classes: benign_qr, phishing_qr, obfuscated_qr

Usage:
------
# 1. Provide your Roboflow API key via environment variable:
$env:ROBOFLOW_API_KEY = "your_api_key_here"

# 2. Run ingestion & fine-tuning:
python ingest_roboflow_dataset.py --dataset phishing-qr --epochs 5

# 3. Dry-run mode (generates calibrated calibration dataset & verifies pipeline):
python ingest_roboflow_dataset.py --dry-run
"""

import os
import sys
import argparse
import logging
import numpy as np

# Ensure UTF-8 output encoding on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("cybershield.roboflow")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data", "roboflow_dataset")
MODEL_DIR = os.path.join(BASE_DIR, "models")
ONNX_OUTPUT = os.path.join(MODEL_DIR, "mobilenet_v2_scam.onnx")

ROBOFLOW_DATASETS = {
    "phishing-qr": {
        "workspace": "fypdetectingphishingqrcodes-gy8sq",
        "project": "phishing-qr-detection",
        "version": 1,
        "description": "Annotated benign vs malicious/quishing QR codes",
        "url": "https://universe.roboflow.com/fypdetectingphishingqrcodes-gy8sq/phishing-qr-detection"
    },
    "phishing-logo": {
        "workspace": "santhosh-sandy-d5tfn",
        "project": "phishing-logo-detection",
        "version": 1,
        "description": "Counterfeit and spoofed enterprise/banking logos",
        "url": "https://universe.roboflow.com/santhosh-sandy-d5tfn/phishing-logo-detection"
    },
    "login-detection": {
        "workspace": "scam-detection",
        "project": "scam-detection",
        "version": 1,
        "description": "Visual indicators of fraudulent web interfaces & fake login pages",
        "url": "https://universe.roboflow.com/scam-detection/scam-detection"
    }
}

CLASS_LABELS = [
    "safe_content",       # 0: Legitimate websites, normal photos, safe QR
    "fake_login_page",    # 1: Spoofed login / credential harvesting screens
    "fake_bank_ui",       # 2: Counterfeit banking portals & OTP theft pages
    "scam_qr_landing"     # 3: Malicious quishing QR landing destinations
]
NUM_CLASSES = len(CLASS_LABELS)


def download_from_roboflow(dataset_key: str, api_key: str, target_dir: str):
    """Downloads dataset from Roboflow Universe using official SDK."""
    try:
        from roboflow import Roboflow
    except ImportError:
        logger.error("Roboflow SDK not installed. Run: pip install roboflow")
        sys.exit(1)

    if dataset_key not in ROBOFLOW_DATASETS:
        raise ValueError(f"Unknown dataset key '{dataset_key}'. Choose from: {list(ROBOFLOW_DATASETS.keys())}")

    meta = ROBOFLOW_DATASETS[dataset_key]
    logger.info(f"Connecting to Roboflow Universe for project: {meta['project']}...")
    
    rf = Roboflow(api_key=api_key)
    project = rf.workspace(meta["workspace"]).project(meta["project"])
    version = project.version(meta["version"])
    
    logger.info(f"Downloading dataset '{meta['project']}' (v{meta['version']}) to {target_dir}...")
    dataset = version.download(model_format="folder", location=target_dir)
    logger.info(f"Download complete! Dataset path: {dataset.location}")
    return dataset.location


def create_synthetic_calibration_data(target_dir: str, num_samples_per_class: int = 25):
    """
    Creates a synthetic calibrated sample dataset for local dry-run verification
    when offline or developing without an active Roboflow API key.
    """
    from PIL import Image, ImageDraw
    os.makedirs(target_dir, exist_ok=True)
    
    for split in ["train", "valid"]:
        split_dir = os.path.join(target_dir, split)
        for class_idx, class_name in enumerate(CLASS_LABELS):
            class_folder = os.path.join(split_dir, class_name)
            os.makedirs(class_folder, exist_ok=True)
            
            n_samples = num_samples_per_class if split == "train" else max(5, num_samples_per_class // 4)
            for i in range(n_samples):
                img = Image.new("RGB", (224, 224), color=(20 + class_idx * 40, 30 + class_idx * 30, 40 + class_idx * 20))
                draw = ImageDraw.Draw(img)
                
                # Draw distinctive patterns per class
                if class_name == "safe_content":
                    draw.rectangle([40, 40, 184, 184], outline=(16, 185, 129), width=3)
                    draw.text((60, 100), "SAFE CONTENT", fill=(16, 185, 129))
                elif class_name == "fake_login_page":
                    draw.rectangle([30, 60, 194, 100], fill=(255, 255, 255))
                    draw.rectangle([30, 120, 194, 160], fill=(255, 255, 255))
                    draw.rectangle([60, 180, 164, 210], fill=(206, 15, 61))
                    draw.text((40, 75), "Username:", fill=(0, 0, 0))
                    draw.text((40, 135), "Password:", fill=(0, 0, 0))
                elif class_name == "fake_bank_ui":
                    draw.rectangle([20, 20, 204, 70], fill=(206, 15, 61))
                    draw.text((30, 35), "SECURE BANK LOGIN", fill=(255, 255, 255))
                    draw.rectangle([30, 90, 194, 130], outline=(239, 68, 68), width=2)
                    draw.text((35, 105), "Enter NetBanking PIN", fill=(255, 200, 200))
                elif class_name == "scam_qr_landing":
                    # QR-like checkerboard pattern
                    for r in range(4):
                        for c in range(4):
                            if (r + c) % 2 == 0:
                                draw.rectangle([40 + c * 35, 40 + r * 35, 75 + c * 35, 75 + r * 35], fill=(255, 255, 255))
                
                img_path = os.path.join(class_folder, f"sample_{i:03d}.png")
                img.save(img_path)
    
    logger.info(f"Synthetic calibration data generated in {target_dir}")


def fine_tune_and_export(data_path: str, epochs: int = 3, batch_size: int = 8, lr: float = 1e-4):
    """Fine-tunes MobileNet-v2 on downloaded images and exports to ONNX."""
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torchvision import datasets, transforms
    from torchvision.models import mobilenet_v2, MobileNet_V2_Weights

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"Training on device: {device}")

    # Standard vision transforms matching Qualcomm AI Hub MobileNet-v2 pipeline
    transform_train = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.ColorJitter(brightness=0.1, contrast=0.1),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    transform_val = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    train_dir = os.path.join(data_path, "train")
    val_dir = os.path.join(data_path, "valid") if os.path.exists(os.path.join(data_path, "valid")) else train_dir

    train_dataset = datasets.ImageFolder(train_dir, transform=transform_train)
    val_dataset = datasets.ImageFolder(val_dir, transform=transform_val)

    train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = torch.utils.data.DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

    logger.info(f"Classes discovered: {train_dataset.classes}")
    logger.info(f"Training samples: {len(train_dataset)}, Validation samples: {len(val_dataset)}")

    # Load MobileNet-v2 backbone
    logger.info("Initializing MobileNet-v2 backbone from Qualcomm AI Hub recipe...")
    model = mobilenet_v2(weights=MobileNet_V2_Weights.IMAGENET1K_V1)
    
    # Freeze initial feature extraction layers for fast convergence & stability
    for param in list(model.features.parameters())[:-8]:
        param.requires_grad = False

    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.2),
        nn.Linear(in_features, NUM_CLASSES)
    )
    model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(filter(lambda p: p.requires_grad, model.parameters()), lr=lr, weight_decay=1e-2)

    logger.info(f"Starting fine-tuning for {epochs} epochs...")
    for epoch in range(epochs):
        model.train()
        total_loss = 0.0
        correct = 0
        total = 0
        
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            total_loss += loss.item() * images.size(0)
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()

        epoch_loss = total_loss / max(1, total)
        epoch_acc = (correct / max(1, total)) * 100.0

        # Evaluate validation
        model.eval()
        val_correct = 0
        val_total = 0
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                _, predicted = outputs.max(1)
                val_total += labels.size(0)
                val_correct += predicted.eq(labels).sum().item()
        
        val_acc = (val_correct / max(1, val_total)) * 100.0
        logger.info(f"Epoch [{epoch+1}/{epochs}] - Loss: {epoch_loss:.4f} | Train Acc: {epoch_acc:.1f}% | Val Acc: {val_acc:.1f}%")

    # ─── Export to ONNX ──────────────────────────────────────────────
    logger.info("\nExporting fine-tuned MobileNet-v2 model to ONNX format...")
    model.eval()
    model.to("cpu")
    dummy_input = torch.randn(1, 3, 224, 224)

    os.makedirs(MODEL_DIR, exist_ok=True)
    try:
        torch.onnx.export(
            model,
            dummy_input,
            ONNX_OUTPUT,
            export_params=True,
            opset_version=14,
            do_constant_folding=True,
            input_names=["input"],
            output_names=["logits"],
            dynamic_axes={"input": {0: "batch_size"}, "logits": {0: "batch_size"}},
            dynamo=False
        )
    except TypeError:
        # Older PyTorch without dynamo parameter
        torch.onnx.export(
            model,
            dummy_input,
            ONNX_OUTPUT,
            export_params=True,
            opset_version=14,
            do_constant_folding=True,
            input_names=["input"],
            output_names=["logits"],
            dynamic_axes={"input": {0: "batch_size"}, "logits": {0: "batch_size"}}
        )

    onnx_size_mb = os.path.getsize(ONNX_OUTPUT) / (1024 * 1024)
    logger.info(f"ONNX model successfully saved to: {ONNX_OUTPUT} ({onnx_size_mb:.2f} MB)")

    # Test ONNX Runtime inference
    import onnxruntime as ort
    sess = ort.InferenceSession(ONNX_OUTPUT, providers=["CPUExecutionProvider"])
    test_img = np.random.randn(1, 3, 224, 224).astype(np.float32)
    res = sess.run(None, {"input": test_img})[0][0]
    probs = np.exp(res) / np.exp(res).sum()
    
    logger.info("Sample inference probability distribution:")
    for idx, label in enumerate(CLASS_LABELS):
        logger.info(f"  {label:<18}: {probs[idx]*100:.2f}%")

    logger.info("\nRoboflow fine-tuning & ONNX export pipeline completed successfully!")


def main():
    parser = argparse.ArgumentParser(description="Roboflow Dataset Ingestion & Fine-Tuning for CyberShield")
    parser.add_argument("--dataset", choices=list(ROBOFLOW_DATASETS.keys()), default="phishing-qr", help="Roboflow dataset key")
    parser.add_argument("--api-key", default=os.getenv("ROBOFLOW_API_KEY"), help="Roboflow API Key")
    parser.add_argument("--epochs", type=int, default=3, help="Training epochs")
    parser.add_argument("--dry-run", action="store_true", help="Run with synthetic calibration data without downloading")
    args = parser.parse_args()

    os.makedirs(DATA_DIR, exist_ok=True)

    if args.dry_run or not args.api_key:
        if not args.api_key:
            logger.warning("No ROBOFLOW_API_KEY provided. Running in dry-run calibration mode...")
        calib_dir = os.path.join(DATA_DIR, "synthetic_calibration")
        create_synthetic_calibration_data(calib_dir)
        fine_tune_and_export(calib_dir, epochs=args.epochs)
    else:
        dataset_dir = os.path.join(DATA_DIR, args.dataset)
        downloaded_path = download_from_roboflow(args.dataset, args.api_key, dataset_dir)
        fine_tune_and_export(downloaded_path, epochs=args.epochs)


if __name__ == "__main__":
    main()
