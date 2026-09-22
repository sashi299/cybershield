"""
CyberShield Text Classifier — DistilBERT ONNX Inference
=======================================================
Runs phishing/scam text classification using a fine-tuned DistilBERT model
via ONNX Runtime. Supports Snapdragon NPU acceleration (QNN EP) with
automatic CPU fallback.

Model: distilbert-base-uncased fine-tuned for binary phishing classification
Format: ONNX (INT8 quantized for NPU, FP32 for CPU fallback)
"""
import os
import time
import logging
import numpy as np
from typing import Optional, Tuple

logger = logging.getLogger("cybershield.text_classifier")

# Module-level singleton
_session = None
_tokenizer = None
_is_loaded = False
_provider_used = "none"


def _load_tokenizer():
    """
    Load the DistilBERT tokenizer.
    Uses HuggingFace transformers tokenizer if available,
    otherwise falls back to a basic vocabulary-based tokenizer.
    """
    global _tokenizer
    try:
        from transformers import AutoTokenizer
        from .npu_config import TOKENIZER_DIR, MODEL_DIR
        
        # Try local saved tokenizer first, then download
        if os.path.exists(TOKENIZER_DIR):
            _tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_DIR)
        else:
            _tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
        logger.info("DistilBERT tokenizer loaded successfully")
    except Exception as e:
        logger.warning(f"Could not load DistilBERT tokenizer: {e}")
        _tokenizer = None


def _load_onnx_session():
    """
    Initialize the ONNX Runtime inference session with the best available
    execution provider (QNN NPU > CPU).
    """
    global _session, _is_loaded, _provider_used
    
    try:
        import onnxruntime as ort
        from .npu_config import (
            TEXT_MODEL_QUANTIZED_PATH, TEXT_MODEL_PATH,
            get_execution_providers
        )
        
        # Prefer quantized model (smaller, faster on NPU)
        model_path = None
        if os.path.exists(TEXT_MODEL_QUANTIZED_PATH):
            model_path = TEXT_MODEL_QUANTIZED_PATH
            logger.info(f"Using quantized text model: {TEXT_MODEL_QUANTIZED_PATH}")
        elif os.path.exists(TEXT_MODEL_PATH):
            model_path = TEXT_MODEL_PATH
            logger.info(f"Using full-precision text model: {TEXT_MODEL_PATH}")
        else:
            logger.warning("No DistilBERT ONNX model found. Text classifier unavailable.")
            return
        
        providers = get_execution_providers()
        sess_options = ort.SessionOptions()
        sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        
        _session = ort.InferenceSession(
            model_path,
            sess_options=sess_options,
            providers=providers
        )
        
        # Log which provider is actually being used
        active = _session.get_providers()
        _provider_used = active[0] if active else "unknown"
        _is_loaded = True
        logger.info(f"DistilBERT ONNX session loaded (provider: {_provider_used})")
        
    except Exception as e:
        logger.error(f"Failed to load DistilBERT ONNX session: {e}")
        _session = None


def load_model():
    """Initialize tokenizer and ONNX session. Called once at startup."""
    _load_tokenizer()
    _load_onnx_session()


def is_available() -> bool:
    """Check if the DistilBERT classifier is ready for inference."""
    return _is_loaded and _session is not None and _tokenizer is not None


def get_provider() -> str:
    """Return the name of the active execution provider."""
    return _provider_used


def predict(text: str) -> Tuple[float, float]:
    """
    Classify text as phishing/scam using DistilBERT.
    
    Args:
        text: The input text to classify
        
    Returns:
        Tuple of (phishing_probability, inference_time_ms)
        phishing_probability: 0.0 (safe) to 1.0 (phishing)
        inference_time_ms: time taken for inference in milliseconds
        
    If the model is unavailable, returns (0.15, 0.0) as a safe-leaning fallback.
    """
    if not is_available():
        # Lazy load on first call
        if not _is_loaded:
            load_model()
        if not is_available():
            return 0.15, 0.0  # Fallback: let rule engine decide
    
    try:
        # Tokenize input
        encoded = _tokenizer(
            text,
            padding="max_length",
            truncation=True,
            max_length=128,
            return_tensors="np"
        )
        
        input_ids = encoded["input_ids"].astype(np.int64)
        attention_mask = encoded["attention_mask"].astype(np.int64)
        
        # Run inference with timing
        start_time = time.perf_counter()
        
        outputs = _session.run(
            None,
            {
                "input_ids": input_ids,
                "attention_mask": attention_mask
            }
        )
        
        inference_ms = (time.perf_counter() - start_time) * 1000
        
        # Extract probability (model outputs logits)
        logits = outputs[0][0]  # Shape: [num_classes]
        
        # Apply softmax to get probabilities
        exp_logits = np.exp(logits - np.max(logits))  # Numerical stability
        probabilities = exp_logits / exp_logits.sum()
        
        # Index 1 = phishing probability
        phishing_prob = float(probabilities[1]) if len(probabilities) > 1 else float(probabilities[0])
        
        logger.debug(f"DistilBERT inference: {phishing_prob:.4f} ({inference_ms:.1f}ms)")
        return phishing_prob, inference_ms
        
    except Exception as e:
        logger.error(f"DistilBERT inference error: {e}")
        return 0.15, 0.0
