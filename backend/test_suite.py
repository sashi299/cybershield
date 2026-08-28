import os
import sys
import unittest
from fastapi.testclient import TestClient

# Ensure app package is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import app
from app.rule_engine import analyze_url_rules, analyze_text_rules
from app.verdict import calculate_verdict

class TestRuleEngine(unittest.TestCase):
    def test_safe_url(self):
        res = analyze_url_rules("https://www.google.com")
        self.assertEqual(len(res["triggered_rules"]), 0)
        self.assertEqual(res["score"], 0)

    def test_typosquatting(self):
        res = analyze_url_rules("http://paypal-security-update.xyz/login")
        rule_ids = [r["rule_id"] for r in res["triggered_rules"]]
        self.assertIn("typosquatting", rule_ids)
        self.assertIn("missing_https", rule_ids)
        self.assertIn("suspicious_tld", rule_ids)

    def test_ip_based_url(self):
        res = analyze_url_rules("http://192.168.1.1/admin/login")
        rule_ids = [r["rule_id"] for r in res["triggered_rules"]]
        self.assertIn("ip_based", rule_ids)

    def test_at_sign_in_url(self):
        res = analyze_url_rules("http://google.com@evil-attacker.com/login")
        rule_ids = [r["rule_id"] for r in res["triggered_rules"]]
        self.assertIn("at_sign", rule_ids)

    def test_excessive_subdomains(self):
        res = analyze_url_rules("http://a.b.c.d.evilbank.com/login")
        rule_ids = [r["rule_id"] for r in res["triggered_rules"]]
        self.assertIn("excessive_subdomains", rule_ids)

    def test_url_shortener(self):
        res = analyze_url_rules("https://bit.ly/claim-prize")
        rule_ids = [r["rule_id"] for r in res["triggered_rules"]]
        self.assertIn("url_shortener", rule_ids)

    def test_data_uri(self):
        res = analyze_url_rules("data:text/html,<script>alert(1)</script>")
        rule_ids = [r["rule_id"] for r in res["triggered_rules"]]
        self.assertIn("data_uri", rule_ids)

    def test_text_rules(self):
        text = "URGENT: Your account is suspended. Click here to confirm your password and claim your prize."
        res = analyze_text_rules(text)
        rule_ids = [r["rule_id"] for r in res["triggered_rules"]]
        self.assertIn("urgency_language", rule_ids)
        self.assertIn("credential_request", rule_ids)
        self.assertIn("prize_scam", rule_ids)

class TestVerdictEngine(unittest.TestCase):
    def test_safe_verdict(self):
        v = calculate_verdict(0, 0.1)
        self.assertEqual(v["verdict"], "Safe")
        self.assertGreaterEqual(v["confidence"], 70.0)

    def test_dangerous_verdict(self):
        v = calculate_verdict(80, 0.9)
        self.assertEqual(v["verdict"], "Dangerous")
        self.assertGreaterEqual(v["confidence"], 80.0)

class TestAPIEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from app.database import init_db
        from app.ml_model import load_model
        init_db()
        load_model()
        cls.client = TestClient(app)

    def test_empty_url_rejected_with_400(self):
        response = self.client.post("/api/analyze/url", json={"url": ""})
        self.assertEqual(response.status_code, 400)
        self.assertIn("empty", response.json()["detail"].lower())

    def test_whitespace_url_rejected_with_400(self):
        response = self.client.post("/api/analyze/url", json={"url": "   "})
        self.assertEqual(response.status_code, 400)

    def test_arbitrary_word_rejected_with_400(self):
        # Passing arbitrary non-URL text like 'hello' or 'banana' should not be analyzed as a website
        response = self.client.post("/api/analyze/url", json={"url": "hello"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("not a valid", response.json()["detail"].lower())

    def test_text_with_spaces_rejected_in_url_tab(self):
        response = self.client.post("/api/analyze/url", json={"url": "this is a message not a url"})
        self.assertEqual(response.status_code, 400)

    def test_empty_text_rejected_with_400(self):
        response = self.client.post("/api/analyze/text", json={"text": "", "type": "email"})
        self.assertEqual(response.status_code, 400)

    def test_valid_phishing_url_analysis(self):
        response = self.client.post("/api/analyze/url", json={"url": "http://paypal-security-update.xyz/login"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["verdict"], "Dangerous")
        self.assertIn("redFlags", data)
        self.assertTrue(len(data["redFlags"]) > 0)
        self.assertIsInstance(data["tips"], list)

    def test_valid_safe_url_analysis(self):
        response = self.client.post("/api/analyze/url", json={"url": "https://www.google.com"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["verdict"], "Safe")

    def test_history_endpoint(self):
        response = self.client.get("/api/history")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_report_endpoint(self):
        # First perform a scan to generate a valid scan_id
        scan_resp = self.client.post("/api/analyze/url", json={"url": "https://example.com"})
        
        # We need to get the history to find the generated scan_id because /analyze/url doesn't return it
        history_resp = self.client.get("/api/history")
        scan_id = history_resp.json()[0]["id"]
        
        response = self.client.post("/api/report", json={"scan_id": scan_id, "comment": "Test threat report"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])

    def test_rate_limit_headers(self):
        response = self.client.get("/api/history")
        self.assertEqual(response.status_code, 200)
        self.assertIn("x-ratelimit-limit", response.headers)
        self.assertIn("x-ratelimit-remaining", response.headers)

class TestFalsePositives(unittest.TestCase):
    """Tests to ensure legitimate messages are not flagged as Dangerous."""
    
    def test_legitimate_bank_otp_not_dangerous(self):
        """Real bank OTP message should not be flagged as Dangerous."""
        text = "Your OTP for SBI Net Banking transaction is 482910. Do not share this OTP with anyone. - SBI"
        res = analyze_text_rules(text)
        # Should have minimal or no flags due to safe context detection
        self.assertLessEqual(res["score"], 30, "Legitimate OTP message should not have high score")
    
    def test_legitimate_delivery_notification_safe(self):
        """Real delivery notification should not be flagged as Dangerous."""
        text = "Your Amazon order #402-1234567-8901234 has shipped and will be delivered by Thursday. Track your package in the Amazon app."
        res = analyze_text_rules(text)
        self.assertLessEqual(res["score"], 20, "Legitimate delivery notification should not have high score")
    
    def test_legitimate_corporate_email_safe(self):
        """Corporate reminder email should not be flagged."""
        text = "Reminder: Please update your quarterly report by end of day Friday. Contact HR if you have questions."
        res = analyze_text_rules(text)
        self.assertLessEqual(res["score"], 20, "Legitimate corporate email should not have high score")
    
    def test_phishing_with_all_signals_still_caught(self):
        """Real phishing with multiple signals should still be caught."""
        text = "URGENT: Your account is suspended. Verify your password immediately or your account will be terminated. Click here: http://paypal-verify.xyz/login"
        res = analyze_text_rules(text)
        self.assertGreaterEqual(res["score"], 30, "Real phishing text should still be detected")


class TestQRDecoder(unittest.TestCase):
    """Tests for QR code decoding with various image types."""
    
    @classmethod
    def setUpClass(cls):
        cls.qr_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_qr_images')
        if not os.path.exists(cls.qr_dir):
            # Generate test images if they don't exist
            from generate_test_qr import generate_test_qr_images
            generate_test_qr_images()
    
    def _read_image(self, filename):
        filepath = os.path.join(self.qr_dir, filename)
        with open(filepath, 'rb') as f:
            return f.read()
    
    def test_qr_standard_url_decode(self):
        """Standard QR code with URL should decode correctly."""
        from app.qr_decoder import decode_qr
        result = decode_qr(self._read_image('standard_url.png'))
        self.assertEqual(result, 'https://www.google.com')
    
    def test_qr_non_url_text_decode(self):
        """QR code with plain text (not a URL) should decode correctly."""
        from app.qr_decoder import decode_qr
        result = decode_qr(self._read_image('plain_text.png'))
        self.assertIn('Hello World', result)
    
    def test_qr_small_image_decode(self):
        """Small QR code should still decode."""
        from app.qr_decoder import decode_qr
        result = decode_qr(self._read_image('small_qr.png'))
        self.assertEqual(result, 'https://example.com')
    
    def test_qr_invalid_image_raises_error(self):
        """Image with no QR code should raise ValueError."""
        from app.qr_decoder import decode_qr
        with self.assertRaises(ValueError):
            decode_qr(self._read_image('no_qr.png'))

if __name__ == "__main__":
    unittest.main(verbosity=2)
