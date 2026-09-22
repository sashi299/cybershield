import os
import cv2
import numpy as np
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("=" * 60)
print("  CYBERSHIELD FULL END-TO-END SANITY TEST PASS")
print("=" * 60)

# 1. System Status Check
print("\n[1/5] Testing System Status & Runtime NPU Detection...")
r = client.get("/api/system/status")
assert r.status_code == 200, f"Expected 200, got {r.status_code}"
status = r.json()
print("  Status:", status)
print(f"  NPU Available: {status['npu_available']}")
print(f"  Execution Provider: {status['execution_provider']}")
print(f"  Models: {status['models_loaded']}")
assert status['models_loaded']['distilbert_onnx'] is True, "DistilBERT ONNX must be loaded"
assert status['models_loaded']['mobilenet_v2_onnx'] is True, "MobileNet-v2 ONNX must be loaded"

# 2. Demo Mode Preset 1: Digital Arrest Scam (SMS)
print("\n[2/5] Testing Demo Preset 1: Digital Arrest Scam (SMS)...")
payload = {
    "text": "URGENT NOTICE: CBI Officer Cyber Crime Branch. An arrest warrant has been issued against your Aadhaar for illegal money laundering. Do not disconnect this call or you will be placed under digital arrest immediately. Transfer funds to safe verification account.",
    "type": "sms"
}
r = client.post("/api/analyze/text", json=payload)
assert r.status_code == 200
res = r.json()
print(f"  Verdict: {res['verdict']} (Confidence: {res['confidence']}%)")
print(f"  Red Flags: {[rf['rule_id'] for rf in res['redFlags']]}")
print(f"  Explanation: {res['explanation'][:80]}...")
assert res['verdict'] == "Dangerous", f"Expected Dangerous, got {res['verdict']}"

# 3. Demo Mode Preset 2: SBI Phishing Link (URL)
print("\n[3/5] Testing Demo Preset 2: SBI Phishing Link (URL)...")
payload = {"url": "http://sbi-netbanking-kyc-update.xyz/login"}
r = client.post("/api/analyze/url", json=payload)
assert r.status_code == 200
res = r.json()
print(f"  Verdict: {res['verdict']} (Confidence: {res['confidence']}%)")
print(f"  Red Flags: {[rf['rule_id'] for rf in res['redFlags']]}")
assert res['verdict'] == "Dangerous", f"Expected Dangerous, got {res['verdict']}"

# 4. Demo Mode Preset 3: Corporate Password Expiry (Email)
print("\n[4/5] Testing Demo Preset 3: Corporate Password Expiry (Email)...")
payload = {
    "text": "ACTION REQUIRED: Your corporate email credentials expire in 2 hours. Verify your account immediately to prevent service interruption: http://company-login-auth.com/portal",
    "type": "email"
}
r = client.post("/api/analyze/text", json=payload)
assert r.status_code == 200
res = r.json()
print(f"  Verdict: {res['verdict']} (Confidence: {res['confidence']}%)")
assert res['verdict'] in ["Suspicious", "Dangerous"], f"Expected Suspicious/Dangerous, got {res['verdict']}"

# 5. Demo Mode Preset 4: Real Bank OTP (SMS)
print("\n[5/5] Testing Demo Preset 4: Real Bank OTP (SMS)...")
payload = {
    "text": "Your OTP for SBI Net Banking transaction is 482910. Valid for 10 minutes. Do not share this OTP with anyone, including bank officials.",
    "type": "sms"
}
r = client.post("/api/analyze/text", json=payload)
assert r.status_code == 200
res = r.json()
print(f"  Verdict: {res['verdict']} (Confidence: {res['confidence']}%)")
assert res['verdict'] == "Safe", f"Expected Safe, got {res['verdict']}"

# 6. QR & Image Drag/Drop/Paste Scan Test
print("\n[Bonus 1] Testing Image / QR Scan with MobileNet-v2 Visual Analysis...")
# Generate a test QR image using OpenCV / qrcode
import qrcode
img = qrcode.make('https://sbi-netbanking-kyc-update.xyz/login')
img_path = 'temp_sanity_qr.png'
img.save(img_path)

with open(img_path, 'rb') as f:
    files = {'file': ('temp_sanity_qr.png', f, 'image/png')}
    r = client.post('/api/analyze/qr', files=files)

if os.path.exists(img_path):
    os.remove(img_path)

assert r.status_code == 200
res = r.json()
print(f"  QR Decoded URL: {res['decoded_url']}")
print(f"  Verdict: {res['verdict']} (Confidence: {res['confidence']}%)")
print(f"  Visual Analysis: {res.get('visual_analysis')}")
assert res.get('visual_analysis') is not None, "Visual analysis from MobileNet-v2 must be present"

# 7. Live Performance Benchmark Test
print("\n[Bonus 2] Testing Live Performance Benchmark Endpoint...")
r = client.get('/api/benchmark')
assert r.status_code == 200
res = r.json()
print(f"  DistilBERT Latency (Avg): {res['text_classifier']['avg_ms']} ms (Provider: {res['text_classifier']['provider']})")
print(f"  MobileNet Latency (Avg): {res['vision_classifier']['avg_ms']} ms (Provider: {res['vision_classifier']['provider']})")

print("\n" + "=" * 60)
print("  ALL SANITY TESTS PASSED! ZERO CRASHES OR REGRESSIONS.")
print("=" * 60)
