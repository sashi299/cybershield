"""
CyberShield Benchmark Utility
=============================
Measures inference latency for text and vision models across
different execution providers (NPU vs CPU).

Usage:
    python -m app.benchmark
    # Or via API: GET /api/benchmark
"""
import time
import json
import os
import logging
import numpy as np
from typing import Dict

logger = logging.getLogger("cybershield.benchmark")

BENCHMARK_RESULTS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "benchmark_results.json"
)

# Sample inputs for benchmarking
SAMPLE_TEXTS = [
    "URGENT: Your SBI NetBanking account has been suspended. Update KYC immediately at http://sbi-kyc-update.com",
    "Your OTP for SBI Net Banking is 482910. Do not share this OTP with anyone.",
    "Congratulations! You won 25 Lakh in KBC Lottery. Call 9876543210 to claim.",
    "Hey bro, are we meeting for lunch at 1 PM today?",
    "Your account will be terminated within 24 hours unless you verify your identity at http://secure-bank-verify.xyz/login",
]


def _create_sample_image() -> bytes:
    """Create a small sample image for vision benchmarking."""
    try:
        import cv2
        # Create a 224x224 random image
        img = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        _, buf = cv2.imencode('.png', img)
        return buf.tobytes()
    except Exception:
        # Minimal valid PNG if cv2 not available
        return b'\x89PNG\r\n\x1a\n' + b'\x00' * 100


def benchmark_text_model(n_runs: int = 50) -> Dict:
    """
    Benchmark the DistilBERT text classifier.
    
    Returns dict with avg/min/max/p50/p95 latency in milliseconds.
    """
    from . import text_classifier
    
    if not text_classifier.is_available():
        text_classifier.load_model()
    
    if not text_classifier.is_available():
        return {"status": "unavailable", "reason": "DistilBERT model not loaded"}
    
    latencies = []
    
    # Warmup run
    text_classifier.predict(SAMPLE_TEXTS[0])
    
    for i in range(n_runs):
        text = SAMPLE_TEXTS[i % len(SAMPLE_TEXTS)]
        _, latency_ms = text_classifier.predict(text)
        latencies.append(latency_ms)
    
    latencies_arr = np.array(latencies)
    
    return {
        "status": "completed",
        "model": "DistilBERT (ONNX)",
        "provider": text_classifier.get_provider(),
        "n_runs": n_runs,
        "avg_ms": round(float(np.mean(latencies_arr)), 2),
        "min_ms": round(float(np.min(latencies_arr)), 2),
        "max_ms": round(float(np.max(latencies_arr)), 2),
        "p50_ms": round(float(np.percentile(latencies_arr, 50)), 2),
        "p95_ms": round(float(np.percentile(latencies_arr, 95)), 2),
    }


def benchmark_vision_model(n_runs: int = 50) -> Dict:
    """
    Benchmark the MobileNet-v2 vision classifier.
    """
    from . import vision_classifier
    
    if not vision_classifier.is_available():
        vision_classifier.load_model()
    
    if not vision_classifier.is_available():
        return {"status": "unavailable", "reason": "MobileNet-v2 model not loaded"}
    
    sample_image = _create_sample_image()
    latencies = []
    
    # Warmup
    vision_classifier.classify_screenshot(sample_image)
    
    for _ in range(n_runs):
        _, latency_ms = vision_classifier.classify_screenshot(sample_image)
        latencies.append(latency_ms)
    
    latencies_arr = np.array(latencies)
    
    return {
        "status": "completed",
        "model": "MobileNet-v2 (ONNX)",
        "provider": vision_classifier.get_provider(),
        "n_runs": n_runs,
        "avg_ms": round(float(np.mean(latencies_arr)), 2),
        "min_ms": round(float(np.min(latencies_arr)), 2),
        "max_ms": round(float(np.max(latencies_arr)), 2),
        "p50_ms": round(float(np.percentile(latencies_arr, 50)), 2),
        "p95_ms": round(float(np.percentile(latencies_arr, 95)), 2),
    }


def run_full_benchmark(n_runs: int = 50) -> Dict:
    """
    Run benchmarks for all models and save results.
    """
    from .npu_config import get_system_status
    
    results = {
        "system": get_system_status(),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "text_classifier": benchmark_text_model(n_runs),
        "vision_classifier": benchmark_vision_model(n_runs),
    }
    
    # Save to file
    try:
        with open(BENCHMARK_RESULTS_PATH, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"Benchmark results saved to {BENCHMARK_RESULTS_PATH}")
    except Exception as e:
        logger.error(f"Could not save benchmark results: {e}")
    
    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Running CyberShield AI Benchmark...")
    results = run_full_benchmark(n_runs=50)
    print(json.dumps(results, indent=2))
