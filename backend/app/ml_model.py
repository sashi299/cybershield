"""
CyberShield ML Model — Hybrid Ensemble (DistilBERT + Legacy TF-IDF)
====================================================================
Provides the unified predict() interface used by the verdict engine.

Priority order:
  1. DistilBERT ONNX model (NPU-accelerated via QNN EP if available)
  2. Legacy TF-IDF + Logistic Regression (scikit-learn .pkl fallback)
  3. Safe-leaning neutral score (0.15) if no model is available

The ensemble combines both scores when both models are available:
  final_prob = 0.7 * distilbert_prob + 0.3 * legacy_prob
"""
import os
import logging
import joblib

logger = logging.getLogger("cybershield.ml_model")

# Legacy model (TF-IDF + Logistic Regression)
LEGACY_MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'phishing_model.pkl')
_legacy_model = None
_legacy_loaded = False

# Track last inference latency for API response
_last_inference_ms = 0.0


def _load_legacy_model():
    """Load the legacy TF-IDF + LogReg model from .pkl file."""
    global _legacy_model, _legacy_loaded
    try:
        if os.path.exists(LEGACY_MODEL_PATH):
            _legacy_model = joblib.load(LEGACY_MODEL_PATH)
            _legacy_loaded = True
            logger.info(f"Legacy ML model loaded from {LEGACY_MODEL_PATH}")
        else:
            logger.warning(f"Legacy model not found at {LEGACY_MODEL_PATH}")
    except Exception as e:
        logger.error(f"Error loading legacy model: {e}")


def _predict_legacy(text: str) -> float:
    """Get phishing probability from the legacy TF-IDF model."""
    global _legacy_model, _legacy_loaded
    if _legacy_model is None and not _legacy_loaded:
        _load_legacy_model()
    if _legacy_model is None:
        return 0.15
    try:
        probabilities = _legacy_model.predict_proba([text])
        if len(probabilities[0]) > 1:
            return float(probabilities[0][1])
        return 0.15
    except Exception:
        return 0.15


def _predict_distilbert(text: str) -> tuple:
    """
    Get phishing probability from DistilBERT ONNX model.
    Returns (probability, inference_ms) or (None, 0.0) if unavailable.
    """
    try:
        from .text_classifier import predict as distilbert_predict, is_available
        if not is_available():
            return None, 0.0
        prob, inference_ms = distilbert_predict(text)
        return prob, inference_ms
    except ImportError:
        return None, 0.0
    except Exception as e:
        logger.error(f"DistilBERT prediction error: {e}")
        return None, 0.0


def load_model():
    """Initialize all available models at startup."""
    global _legacy_model, _legacy_loaded
    
    # Load legacy model
    _load_legacy_model()
    
    # Try to load DistilBERT ONNX model
    try:
        from .text_classifier import load_model as load_distilbert
        load_distilbert()
    except ImportError:
        logger.info("DistilBERT text classifier module not available")
    except Exception as e:
        logger.warning(f"Could not load DistilBERT: {e}")
    
    # Print status
    if _legacy_loaded:
        print(f"ML model loaded successfully from {LEGACY_MODEL_PATH}")


def predict(text: str) -> float:
    """
    Returns probability that the text is phishing (0.0 = safe, 1.0 = phishing).
    
    Uses an ensemble approach:
      - If DistilBERT is available: 70% DistilBERT + 30% Legacy
      - If only legacy is available: 100% Legacy
      - If nothing is available: returns 0.15 (safe-leaning neutral)
    """
    global _last_inference_ms
    
    # Try DistilBERT first
    distilbert_prob, inference_ms = _predict_distilbert(text)
    _last_inference_ms = inference_ms
    
    # Get legacy prediction
    legacy_prob = _predict_legacy(text)
    
    # Ensemble or fallback
    if distilbert_prob is not None:
        # Ensemble: 70% DistilBERT + 30% Legacy
        final_prob = 0.7 * distilbert_prob + 0.3 * legacy_prob
        logger.debug(f"Ensemble: DistilBERT={distilbert_prob:.3f}, Legacy={legacy_prob:.3f}, Final={final_prob:.3f}")
        return final_prob
    else:
        # Legacy-only fallback
        return legacy_prob


def get_last_inference_ms() -> float:
    """Return the inference time of the last prediction (for API response)."""
    return _last_inference_ms
