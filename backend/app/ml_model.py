import os
import joblib

MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'phishing_model.pkl')
model = None
_model_loaded = False

def load_model():
    global model, _model_loaded
    try:
        if os.path.exists(MODEL_PATH):
            model = joblib.load(MODEL_PATH)
            _model_loaded = True
            print(f"ML model loaded successfully from {MODEL_PATH}")
        else:
            print(f"ML model file not found at {MODEL_PATH}")
    except Exception as e:
        print(f"Error loading model: {e}")

def predict(text: str) -> float:
    """
    Returns probability that the text is phishing (0.0 = safe, 1.0 = phishing).
    If the model is unavailable, returns 0.15 (safe-leaning neutral)
    so the verdict engine relies on deterministic rule-engine signals instead.
    """
    if model is None:
        load_model()
    if model is None:
        return 0.15  # Safe-leaning fallback when model unavailable
    try:
        probabilities = model.predict_proba([text])
        if len(probabilities[0]) > 1:
            return float(probabilities[0][1])
        return 0.15
    except Exception:
        return 0.15

