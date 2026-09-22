"""
CyberShield Vision Classifier — MobileNet-v2 ONNX Inference
============================================================
Classifies QR code images and screenshots for visual scam indicators
(fake bank UIs, spoofed login pages, etc.) using MobileNet-v2 via
ONNX Runtime with Snapdragon NPU support.

Model: MobileNet-v2 with custom 4-class head
Classes: safe_content, fake_login_page, fake_bank_ui, scam_qr_landing
Format: ONNX (quantized W8A16 for NPU)
"""
import os
import time
import logging
import numpy as np
from typing import Optional, Tuple, Dict

logger = logging.getLogger("cybershield.vision_classifier")

# Module-level singleton
_session = None
_is_loaded = False
_provider_used = "none"

# Classification labels
CLASS_LABELS = [
    "safe_content",
    "fake_login_page",
    "fake_bank_ui",
    "scam_qr_landing"
]


def _load_onnx_session():
    """Initialize MobileNet-v2 ONNX Runtime session."""
    global _session, _is_loaded, _provider_used
    
    try:
        import onnxruntime as ort
        from .npu_config import VISION_MODEL_PATH, get_execution_providers
        
        if not os.path.exists(VISION_MODEL_PATH):
            logger.warning(f"Vision model not found at {VISION_MODEL_PATH}. Visual scam detection unavailable.")
            return
        
        providers = get_execution_providers()
        sess_options = ort.SessionOptions()
        sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        
        _session = ort.InferenceSession(
            VISION_MODEL_PATH,
            sess_options=sess_options,
            providers=providers
        )
        
        active = _session.get_providers()
        _provider_used = active[0] if active else "unknown"
        _is_loaded = True
        logger.info(f"MobileNet-v2 vision model loaded (provider: {_provider_used})")
        
    except Exception as e:
        logger.error(f"Failed to load MobileNet-v2 ONNX session: {e}")
        _session = None


def load_model():
    """Initialize the vision classifier. Called once at startup."""
    _load_onnx_session()


def is_available() -> bool:
    """Check if the vision classifier is ready."""
    return _is_loaded and _session is not None


def get_provider() -> str:
    """Return the active execution provider."""
    return _provider_used


def preprocess_image(image_bytes: bytes) -> Optional[np.ndarray]:
    """
    Preprocess an image for MobileNet-v2 inference.
    Resizes to 224x224, normalizes to ImageNet mean/std.
    
    Args:
        image_bytes: Raw image bytes (PNG/JPG)
        
    Returns:
        Preprocessed numpy array of shape [1, 3, 224, 224] or None on failure
    """
    try:
        import cv2
        
        # Decode image from bytes
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            logger.warning("Could not decode image bytes")
            return None
        
        # Resize to 224x224 (MobileNet-v2 input size)
        img = cv2.resize(img, (224, 224))
        
        # Convert BGR to RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Normalize to [0, 1] then apply ImageNet normalization
        img = img.astype(np.float32) / 255.0
        mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
        img = (img - mean) / std
        
        # Transpose to CHW format: [H, W, C] -> [C, H, W]
        img = np.transpose(img, (2, 0, 1))
        
        # Add batch dimension: [C, H, W] -> [1, C, H, W]
        img = np.expand_dims(img, axis=0)
        
        return img
        
    except Exception as e:
        logger.error(f"Image preprocessing error: {e}")
        return None


def classify_screenshot(image_bytes: bytes) -> Tuple[Dict, float]:
    """
    Classify an image/screenshot for visual scam indicators.
    
    Args:
        image_bytes: Raw image bytes
        
    Returns:
        Tuple of (result_dict, inference_time_ms)
        result_dict: {"class": str, "confidence": float, "all_scores": dict}
    """
    if not is_available():
        if not _is_loaded:
            load_model()
        if not is_available():
            return {"class": "unknown", "confidence": 0.0, "all_scores": {}}, 0.0
    
    try:
        # Preprocess
        input_tensor = preprocess_image(image_bytes)
        if input_tensor is None:
            return {"class": "unknown", "confidence": 0.0, "all_scores": {}}, 0.0
        
        # Get input name from model
        input_name = _session.get_inputs()[0].name
        
        # Run inference with timing
        start_time = time.perf_counter()
        
        outputs = _session.run(None, {input_name: input_tensor})
        
        inference_ms = (time.perf_counter() - start_time) * 1000
        
        # Apply softmax to logits
        logits = outputs[0][0]
        exp_logits = np.exp(logits - np.max(logits))
        probabilities = exp_logits / exp_logits.sum()
        
        # Get top prediction
        top_idx = int(np.argmax(probabilities))
        top_class = CLASS_LABELS[top_idx] if top_idx < len(CLASS_LABELS) else "unknown"
        top_confidence = float(probabilities[top_idx])
        
        # Build all scores dict
        all_scores = {}
        for i, label in enumerate(CLASS_LABELS):
            if i < len(probabilities):
                all_scores[label] = round(float(probabilities[i]), 4)
        
        result = {
            "class": top_class,
            "confidence": round(top_confidence, 4),
            "all_scores": all_scores
        }
        
        logger.debug(f"Vision inference: {top_class} ({top_confidence:.4f}, {inference_ms:.1f}ms)")
        return result, inference_ms
        
    except Exception as e:
        logger.error(f"Vision classification error: {e}")
        return {"class": "unknown", "confidence": 0.0, "all_scores": {}}, 0.0
