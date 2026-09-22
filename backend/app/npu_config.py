"""
CyberShield NPU Configuration
=============================
Central configuration for Snapdragon NPU acceleration via ONNX Runtime.
Detects available execution providers (QNN for Snapdragon NPU, or CPU fallback)
and provides model path constants.

Environment Variables:
  CYBERSHIELD_EP: Force execution provider ('qnn', 'cpu', or 'auto' [default])
  CYBERSHIELD_MODEL_DIR: Override model directory path
"""
import os
import logging

logger = logging.getLogger("cybershield.npu")

# Model directory (default: backend/models/)
MODEL_DIR = os.environ.get(
    "CYBERSHIELD_MODEL_DIR",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
)

# Model file paths
TEXT_MODEL_PATH = os.path.join(MODEL_DIR, "distilbert_phishing.onnx")
TEXT_MODEL_QUANTIZED_PATH = os.path.join(MODEL_DIR, "distilbert_phishing_int8.onnx")
VISION_MODEL_PATH = os.path.join(MODEL_DIR, "mobilenet_v2_scam.onnx")
LEGACY_MODEL_PATH = os.path.join(MODEL_DIR, "phishing_model.pkl")
TOKENIZER_DIR = os.path.join(MODEL_DIR, "tokenizer")

# Execution provider preference
_EP_PREFERENCE = os.environ.get("CYBERSHIELD_EP", "auto").lower()

def _check_qnn_available() -> bool:
    """Check if QNN (Qualcomm Neural Network) Execution Provider is available."""
    try:
        import onnxruntime as ort
        available_providers = ort.get_available_providers()
        # Check for QNN EP (available on Snapdragon PCs with onnxruntime-qnn installed)
        if "QNNExecutionProvider" in available_providers:
            return True
        # Also try the plugin-based registration approach (onnxruntime-qnn >= 2.0)
        try:
            import onnxruntime_qnn
            return True
        except ImportError:
            pass
        return False
    except ImportError:
        return False

def get_execution_providers() -> list:
    """
    Returns the ordered list of ONNX Runtime execution providers to use.
    On Snapdragon PCs with QNN EP: ['QNNExecutionProvider', 'CPUExecutionProvider']
    On other hardware: ['CPUExecutionProvider']
    """
    if _EP_PREFERENCE == "cpu":
        logger.info("Execution provider forced to CPU via CYBERSHIELD_EP env var")
        return ["CPUExecutionProvider"]
    
    if _EP_PREFERENCE == "qnn" or _EP_PREFERENCE == "auto":
        if _check_qnn_available():
            logger.info("Snapdragon NPU detected! Using QNN Execution Provider for hardware acceleration.")
            try:
                import onnxruntime_qnn as qnn_ep
                # Plugin-based QNN EP (onnxruntime-qnn >= 2.0)
                import onnxruntime as ort
                ep_lib_path = qnn_ep.get_library_path()
                ort.register_execution_provider_library("QNNExecutionProvider", ep_lib_path)
                return [
                    ("QNNExecutionProvider", {"backend_path": qnn_ep.get_qnn_htp_path()}),
                    "CPUExecutionProvider"
                ]
            except Exception as e:
                logger.warning(f"QNN EP plugin registration failed: {e}. Trying direct provider.")
                return ["QNNExecutionProvider", "CPUExecutionProvider"]
        elif _EP_PREFERENCE == "qnn":
            logger.warning("QNN EP requested but not available. Install onnxruntime-qnn on a Snapdragon PC.")
    
    logger.info("Using CPU Execution Provider (no Snapdragon NPU detected)")
    return ["CPUExecutionProvider"]

def is_npu_available() -> bool:
    """Check if Snapdragon NPU acceleration is available."""
    return _check_qnn_available()

def get_active_provider_name() -> str:
    """Returns a human-readable name of the active execution provider."""
    providers = get_execution_providers()
    first = providers[0] if providers else "Unknown"
    if isinstance(first, tuple):
        first = first[0]
    if "QNN" in first:
        return "Snapdragon NPU (QNN)"
    return "CPU"

def get_system_status() -> dict:
    """Returns full system status for the /api/system/status endpoint."""
    import platform
    models_loaded = {
        "distilbert_onnx": os.path.exists(TEXT_MODEL_PATH) or os.path.exists(TEXT_MODEL_QUANTIZED_PATH),
        "mobilenet_v2_onnx": os.path.exists(VISION_MODEL_PATH),
        "legacy_tfidf": os.path.exists(LEGACY_MODEL_PATH),
    }
    return {
        "npu_available": is_npu_available(),
        "execution_provider": get_active_provider_name(),
        "platform": platform.machine(),
        "processor": platform.processor(),
        "models_loaded": models_loaded,
        "model_dir": MODEL_DIR,
    }
