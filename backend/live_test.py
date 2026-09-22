import requests

base = 'http://localhost:8000/api'

tests = [
    ('Phishing URL', 'post', f'{base}/analyze/url', {'url': 'http://paypal-security-update.xyz/login'}, 'Dangerous'),
    ('Safe URL', 'post', f'{base}/analyze/url', {'url': 'https://google.com'}, 'Safe'),
    ('Bank Phishing SMS', 'post', f'{base}/analyze/text', {'text': 'URGENT: SBI NetBanking account blocked. Update KYC at http://sbi-kyc-update.com', 'type': 'sms'}, 'Dangerous'),
    ('Real Bank OTP', 'post', f'{base}/analyze/text', {'text': 'Your OTP for SBI Net Banking is 482910. Do not share this OTP with anyone. - SBI', 'type': 'sms'}, 'Safe'),
    ('Lottery Scam', 'post', f'{base}/analyze/text', {'text': 'Congratulations! You won 25 Lakh in KBC Lottery. Call 9876543210 to claim.', 'type': 'sms'}, 'Dangerous'),
    ('Normal Chat', 'post', f'{base}/analyze/text', {'text': 'Hey bro, are we meeting for lunch at 1 PM today?', 'type': 'sms'}, 'Safe'),
    ('Invalid URL', 'post', f'{base}/analyze/url', {'url': 'asdfghjkl'}, 'Safe'),
    ('Empty Text', 'post', f'{base}/analyze/text', {'text': '', 'type': 'sms'}, None),
]

print('=' * 70)
print('  CYBERSHIELD FULL LIVE INTEGRATION TEST')
print('=' * 70)

passed = 0
failed = 0

for name, method, url, payload, expected in tests:
    try:
        if method == 'post':
            r = requests.post(url, json=payload, timeout=15)
        else:
            r = requests.get(url, timeout=15)

        data = r.json()
        verdict = data.get('verdict', '')
        confidence = data.get('confidence', 0)
        explanation = (data.get('explanation', '') or '')[:80]
        tips = data.get('tips', [])
        recommendation = data.get('recommendation', '') or ''

        # Check verdict match
        if expected is None:
            # Expect error response (400)
            ok = r.status_code == 400
        elif expected == 'Dangerous':
            ok = verdict in ('Dangerous', 'Suspicious')
        else:
            ok = verdict == expected

        # Check explanation and tips are not empty for valid scans
        if expected and expected != 'Safe' and ok:
            if not explanation.strip():
                ok = False
                print(f'  [WARN] {name}: Empty explanation!')
            if not tips:
                ok = False
                print(f'  [WARN] {name}: Empty tips!')

        status = 'PASS' if ok else 'FAIL'
        if ok:
            passed += 1
        else:
            failed += 1

        if verdict:
            print(f'  [{status}] {name}: {verdict} ({confidence}%)')
            print(f'         Explanation: {explanation}...')
            print(f'         Tips: {len(tips)} tips | Recommendation: {recommendation[:60]}')
        else:
            print(f'  [{status}] {name}: HTTP {r.status_code} (expected error)')

    except Exception as e:
        failed += 1
        print(f'  [FAIL] {name}: {e}')

# Test History endpoint
try:
    r = requests.get(f'{base}/history', timeout=10)
    data = r.json()
    print(f'  [PASS] History: {len(data)} records returned')
    passed += 1
except Exception as e:
    print(f'  [FAIL] History: {e}')
    failed += 1

print('=' * 70)
total = passed + failed
if failed == 0:
    print(f'  RESULT: ALL {total} TESTS PASSED - ZERO BUGS FOUND!')
else:
    print(f'  RESULT: {passed}/{total} passed, {failed} FAILED')
print('=' * 70)
