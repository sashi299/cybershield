import unittest
import os
import numpy as np

class TestSnapdragonNPU(unittest.TestCase):
    def test_npu_config_status(self):
        from app.npu_config import get_system_status, is_npu_available, get_execution_providers
        status = get_system_status()
        self.assertIn("npu_available", status)
        self.assertIn("execution_provider", status)
        self.assertIn("models_loaded", status)
        self.assertTrue(status["models_loaded"]["distilbert_onnx"])
        self.assertTrue(status["models_loaded"]["mobilenet_v2_onnx"])
        
        providers = get_execution_providers()
        self.assertTrue(len(providers) >= 1)

    def test_distilbert_text_classifier(self):
        from app import text_classifier
        if not text_classifier.is_available():
            text_classifier.load_model()
        self.assertTrue(text_classifier.is_available())
        
        # Test safe text
        prob_safe, ms_safe = text_classifier.predict("Hello team, please find attached the meeting notes.")
        self.assertIsInstance(prob_safe, float)
        self.assertTrue(0.0 <= prob_safe <= 1.0)
        self.assertTrue(ms_safe > 0.0)

        # Test phishing text
        prob_phish, ms_phish = text_classifier.predict("URGENT: Your account has been suspended! Click http://fake-login.xyz to verify password immediately.")
        self.assertIsInstance(prob_phish, float)
        self.assertTrue(0.0 <= prob_phish <= 1.0)

    def test_mobilenet_vision_classifier(self):
        from app import vision_classifier
        if not vision_classifier.is_available():
            vision_classifier.load_model()
        self.assertTrue(vision_classifier.is_available())
        
        # Test with dummy image
        import cv2
        dummy_img = np.zeros((224, 224, 3), dtype=np.uint8)
        _, buf = cv2.imencode('.png', dummy_img)
        
        res, ms = vision_classifier.classify_screenshot(buf.tobytes())
        self.assertIn("class", res)
        self.assertIn("confidence", res)
        self.assertIn("all_scores", res)
        self.assertIn(res["class"], vision_classifier.CLASS_LABELS)
        self.assertTrue(ms > 0.0)

    def test_system_status_endpoint(self):
        from fastapi.testclient import TestClient
        from app.main import app
        client = TestClient(app)
        response = client.get("/api/system/status")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("npu_available", data)
        self.assertIn("execution_provider", data)

    def test_benchmark_endpoint(self):
        from fastapi.testclient import TestClient
        from app.main import app
        client = TestClient(app)
        response = client.get("/api/benchmark")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("text_classifier", data)
        self.assertIn("vision_classifier", data)

if __name__ == '__main__':
    unittest.main()
