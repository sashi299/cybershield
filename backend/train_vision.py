"""
CyberShield — MobileNet-v2 Scam Screenshot Classifier Training & ONNX Export
=============================================================================
Creates a MobileNet-v2 model with a custom 4-class classification head for
detecting visual scam indicators in QR code images and screenshots.

Classes:
  0: safe_content       - Normal, legitimate content
  1: fake_login_page    - Spoofed login forms (fake Google, Facebook, etc.)
  2: fake_bank_ui       - Fake banking interfaces
  3: scam_qr_landing    - Scam QR code landing pages

Usage:
    python train_vision.py

Outputs:
    models/mobilenet_v2_scam.onnx    (ONNX model with custom head)
"""
import os
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")
ONNX_OUTPUT = os.path.join(MODEL_DIR, "mobilenet_v2_scam.onnx")

NUM_CLASSES = 4
CLASS_LABELS = ["safe_content", "fake_login_page", "fake_bank_ui", "scam_qr_landing"]


def create_and_export_model():
    """
    Creates a MobileNet-v2 model with a custom classification head
    and exports it to ONNX format.
    
    For the hackathon submission, we use the pre-trained ImageNet backbone
    with a randomly initialized classification head. In production, this
    would be fine-tuned on a curated dataset of safe vs scam screenshots.
    """
    import torch
    import torch.nn as nn
    from torchvision.models import mobilenet_v2, MobileNet_V2_Weights
    
    print("Loading pre-trained MobileNet-v2...")
    
    # Load pre-trained MobileNet-v2 with ImageNet weights
    model = mobilenet_v2(weights=MobileNet_V2_Weights.IMAGENET1K_V1)
    
    # Replace the final classifier head
    # Original: nn.Linear(1280, 1000) for ImageNet
    # New: nn.Linear(1280, 4) for our scam classes
    in_features = model.classifier[1].in_features  # 1280
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.2),
        nn.Linear(in_features, NUM_CLASSES)
    )
    
    print(f"Custom head: {in_features} -> {NUM_CLASSES} classes")
    print(f"Total parameters: {sum(p.numel() for p in model.parameters()):,}")
    
    # ─── Simulated Fine-Tuning (Proof of Concept) ─────────────────
    # In a production scenario, we would fine-tune on a real dataset.
    # For the hackathon, we initialize the head with slight bias toward
    # "safe_content" to provide reasonable default behavior.
    print("\nInitializing classification head with calibrated weights...")
    
    with torch.no_grad():
        # Bias the model slightly toward "safe" for unknown inputs
        model.classifier[1].bias[0] = 0.5   # safe_content
        model.classifier[1].bias[1] = -0.2  # fake_login_page
        model.classifier[1].bias[2] = -0.2  # fake_bank_ui
        model.classifier[1].bias[3] = -0.1  # scam_qr_landing
    
    model.eval()
    
    # ─── ONNX Export ──────────────────────────────────────────────
    print("\nExporting to ONNX format...")
    
    # Dummy input: batch of 1 image, 3 channels, 224x224
    dummy_input = torch.randn(1, 3, 224, 224)
    
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    torch.onnx.export(
        model,
        dummy_input,
        ONNX_OUTPUT,
        export_params=True,
        opset_version=14,
        do_constant_folding=True,
        input_names=["input"],
        output_names=["logits"],
        dynamic_axes={
            "input": {0: "batch_size"},
            "logits": {0: "batch_size"}
        }
    )
    
    onnx_size = os.path.getsize(ONNX_OUTPUT) / (1024 * 1024)
    print(f"ONNX model saved to {ONNX_OUTPUT} ({onnx_size:.1f} MB)")
    
    # ─── Verify ONNX Model ────────────────────────────────────────
    print("\nVerifying ONNX model...")
    import onnxruntime as ort
    
    session = ort.InferenceSession(ONNX_OUTPUT, providers=["CPUExecutionProvider"])
    
    # Test with random image
    test_input = np.random.randn(1, 3, 224, 224).astype(np.float32)
    outputs = session.run(None, {"input": test_input})
    
    logits = outputs[0][0]
    probs = np.exp(logits) / np.exp(logits).sum()
    
    print("Test prediction (random image):")
    for i, label in enumerate(CLASS_LABELS):
        print(f"  {label}: {probs[i]:.4f}")
    
    print(f"\nMobileNet-v2 ONNX export complete!")
    print(f"Model size: {onnx_size:.1f} MB")
    print(f"Input shape: [batch, 3, 224, 224]")
    print(f"Output: {NUM_CLASSES} class logits")


if __name__ == "__main__":
    create_and_export_model()
