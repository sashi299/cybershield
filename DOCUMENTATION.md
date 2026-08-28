# 🛡️ Cyber Shield — Comprehensive Project Documentation

**An Intelligent Phishing, Scam & Cyber-Fraud Detection Platform**  
*Built for HackSprint 2.0 Hackathon*

---

## 📑 Table of Contents
1. [Executive Summary](#1-executive-summary)
2. [System Architecture](#2-system-architecture)
3. [Detection Pipeline](#3-detection-pipeline)
   - 3.1 [Rule-Based Heuristic Engine](#31-rule-based-heuristic-engine)
   - 3.2 [Machine Learning Classifier](#32-machine-learning-classifier)
   - 3.3 [QR Code Decoding Engine](#33-qr-code-decoding-engine)
   - 3.4 [Combined Verdict Engine](#34-combined-verdict-engine)
   - 3.5 [Plain-Language Explanation & Security Tips](#35-plain-language-explanation--security-tips)
4. [Tech Stack](#4-tech-stack)
5. [Project Structure](#5-project-structure)
6. [API Reference & Endpoints](#6-api-reference--endpoints)
7. [Installation & Setup Guide](#7-installation--setup-guide)
8. [Machine Learning & Benchmarking](#8-machine-learning--benchmarking)
9. [Security & Optimization Features](#9-security--optimization-features)
10. [Automated Testing Suite](#10-automated-testing-suite)

---

## 1. Executive Summary

Phishing attacks, SMS scams (smishing), fraudulent emails, and malicious QR codes (quishing) target everyday internet users who lack specialized cybersecurity knowledge. 

**Cyber Shield** is an intelligent full-stack security platform that:
- Ingests multiple digital inputs: **URLs**, **Email Text**, **SMS Text**, and **QR Code Images**.
- Employs a **hybrid detection engine** (Heuristic Rules + TF-IDF Machine Learning Classifier).
- Calculates a weighted risk score and categorizes it into **Safe**, **Suspicious**, or **Dangerous**.
- Translates technical vulnerabilities into **plain-language explanations**, provides **tailored recommendations**, and offers **educational awareness tips**.
- Provides a centralized **History Dashboard** and a **Threat Reporting** mechanism backed by SQLite.

---

## 2. System Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                      React 18 + Vite 6 Frontend                          │
│          Tailwind CSS · Lucide Icons · Axios · Responsive Dark UI        │
└────────────────────────────────────┬─────────────────────────────────────┘
                                     │ REST API (JSON / Multipart)
┌────────────────────────────────────▼─────────────────────────────────────┐
│                       FastAPI Backend Core (Python)                      │
│                                                                          │
│  ┌───────────────────────┐   ┌────────────────────────────────────────┐  │
│  │ Rate Limit Middleware │   │ CORS Middleware (Configurable Whitelist│  │
│  └───────────┬───────────┘   └───────────────────┬────────────────────┘  │
│              └─────────────────┬─────────────────┘                       │
│                                │                                         │
│         ┌──────────────────────┴──────────────────────┐                  │
│         │              API Router (routes.py)         │                  │
│         └──────┬───────────────────┬──────────────────┘                  │
│                │                   │                                     │
│  ┌─────────────▼─────────┐   ┌─────▼──────────────────┐                  │
│  │   Rule-Based Engine   │   │  ML TF-IDF Classifier  │                  │
│  │  (15+ URL & 6 Text)   │   │  (Logistic Regression) │                  │
│  └─────────────┬─────────┘   └─────┬──────────────────┘                  │
│                │                   │                                     │
│                └─────────┬─────────┘                                     │
│                          │                                               │
│             ┌────────────▼───────────┐      ┌─────────────────────────┐  │
│             │ Combined Verdict Engine├──────┤  QR Decoder (pyzbar/CV) │  │
│             └────────────┬───────────┘      └─────────────────────────┘  │
│                          │                                               │
│             ┌────────────▼───────────┐      ┌─────────────────────────┐  │
│             │  Explainer & Tips Gen  ├──────┤    SQLite Database      │  │
│             └────────────────────────┘      │       (WAL Mode)        │  │
│                                             └─────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Detection Pipeline

### 3.1 Rule-Based Heuristic Engine (`rule_engine.py`)
Analyzes digital content using deterministic pattern matching and heuristic rules:

| Rule Name | Severity | Description / Trigger Condition |
| :--- | :--- | :--- |
| `typosquatting` | **HIGH** | Detects deceptive lookalikes of popular domains (Google, PayPal, Amazon, Netflix, Apple, Banks, etc.). |
| `ip_based` | **HIGH** | URL uses a raw IP address (e.g., `192.168.1.1`) instead of a registered domain. |
| `at_sign` | **HIGH** | URL contains `@` symbol used to obfuscate the real destination server. |
| `data_uri` | **HIGH** | URL uses `data:` scheme (used in phishing payload delivery). |
| `suspicious_tld` | **MEDIUM** | Uses spam/abuse-heavy TLDs (`.xyz`, `.tk`, `.ml`, `.ga`, `.click`, `.club`, etc.). |
| `url_shortener` | **MEDIUM** | Uses shortening services (`bit.ly`, `tinyurl.com`, `t.co`, `is.gd`, `ow.ly`). |
| `excessive_subdomains` | **MEDIUM** | URL contains $> 4$ subdomain segments (e.g., `a.b.c.d.bank.com`). |
| `suspicious_keyword` | **HIGH** | URL contains terms like `verify`, `suspended`, `urgent`, `compromised`, etc. |
| `missing_https` | **LOW** | Missing SSL/TLS encryption (`http://` instead of `https://`). |
| `urgency_language` | **HIGH** | Text contains pressure words (`immediate action required`, `act now`, `click here`). |
| `prize_scam` | **HIGH** | Text promises fake rewards (`congratulations`, `winner`, `won a prize`, `lottery`). |
| `financial_request` | **HIGH** | Text asks for `credit card`, `CVV`, `PIN`, `bank account`, or `SSN`. |
| `credential_request`| **HIGH** | Text asks for `password`, `OTP`, or `verification code`. |
| `threat_language` | **HIGH** | Text threatens consequences (`account will be closed`, `legal action`). |
| `impersonation` | **MEDIUM** | Uses generic impersonating salutations (`Dear customer`, `Dear user`). |

### 3.2 Machine Learning Classifier (`ml_model.py` & `train_model.py`)
- **Feature Extraction**: Character n-grams ($3 \le n \le 5$) with TF-IDF Vectorization to capture sub-word patterns, brand misspellings, and keyword fragments.
- **Classifier Algorithm**: Scikit-Learn `LogisticRegression` pipeline with calibrated probability output (`predict_proba`).
- **Resilience**: Gracefully returns neutral 0.5 probability if the model file is not yet loaded.

### 3.3 QR Code Decoding Engine (`qr_decoder.py`)
- Ingests uploaded image bytes (PNG, JPEG, WebP).
- Uses `pyzbar` for initial fast decoding.
- Automatically applies OpenCV fallback preprocessing (Grayscale conversion + Otsu adaptive binary thresholding) for low-contrast or noisy images.
- Extracted URLs are piped directly through the full URL inspection engine.

### 3.4 Combined Verdict Engine (`verdict.py`)
The system computes a hybrid weighted risk score:

$$\text{Combined Score} = (0.40 \times \text{Rule Score}) + (0.60 \times (\text{ML Probability} \times 100))$$

$$\text{Verdict} = \begin{cases} 
\textbf{Safe} & \text{if Combined Score} < 30 \\ 
\textbf{Suspicious} & \text{if } 30 \le \text{Combined Score} \le 65 \\ 
\textbf{Dangerous} & \text{if Combined Score} > 65 
\end{cases}$$

Confidence score is calibrated and rounded to 1 decimal place:
$$\text{Confidence} = \text{round}\Big(\max(\text{Combined Score}, 100 - \text{Combined Score}), 1\Big)$$

### 3.5 Plain-Language Explanation & Security Tips (`explainer.py`)
Transforms detected red flags into human-friendly bullet points, supplies threat-category specific recommendations (e.g. *Email Scam vs. Smishing vs. Phishing URL*), and presents 2–3 actionable safety tips.

---

## 4. Tech Stack

| Layer | Technology | Key Libraries / Modules |
| :--- | :--- | :--- |
| **Frontend** | React 18 (Vite 6) | Tailwind CSS 4, React Router 7, Lucide React, Axios |
| **Backend API** | Python 3.10+ (FastAPI) | Uvicorn, Starlette, Pydantic v2 |
| **Machine Learning** | Scikit-Learn | TF-IDF Vectorizer, Logistic Regression, Joblib, Pandas, NumPy |
| **QR Processing** | PyZBar & OpenCV | `pyzbar`, `opencv-python-headless`, Pillow |
| **Database** | SQLite3 | WAL (Write-Ahead Logging) Mode |
| **Testing** | Python Unittest & TestClient | `unittest`, `fastapi.testclient`, `httpx` |

---

## 5. Project Structure

```
cybershield/
├── README.md                      # Quickstart documentation
├── DOCUMENTATION.md               # Detailed architecture & API documentation
├── TESTING_REPORT.txt             # Verified test execution log (100% pass)
├── .gitignore                     # Git exclusion rules
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                # FastAPI app initialization, CORS & middlewares
│   │   ├── database.py            # SQLite schema initialization with WAL mode
│   │   ├── rate_limiter.py        # Sliding-window IP rate limiting middleware
│   │   ├── rule_engine.py         # Heuristic rule-based detection engine
│   │   ├── ml_model.py            # ML pipeline inference module
│   │   ├── qr_decoder.py          # PyZBar and OpenCV QR image decoder
│   │   ├── verdict.py             # Weighted score combiner and verdict calculator
│   │   ├── explainer.py           # Plain-English explanations and tips generator
│   │   └── routes.py              # REST API endpoints with request validation
│   ├── data/
│   │   └── phishing_dataset.csv   # Training dataset (400 samples)
│   ├── models/
│   │   └── phishing_model.pkl     # Trained ML pipeline model
│   ├── train_model.py             # Standalone model training script
│   ├── benchmark_ml.py            # Comprehensive ML evaluation & benchmark script
│   ├── test_suite.py              # Automated test suite (28 unit & integration tests)
│   ├── requirements.txt           # Python dependencies
│   └── test_qr.png                # Sample QR image for automated tests
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── Header.jsx         # Navigation bar with branding
    │   │   ├── Footer.jsx         # Footer with HackSprint info
    │   │   ├── InputTabs.jsx      # Multi-modal input tabs (URL, Email, SMS, QR)
    │   │   ├── RiskMeter.jsx      # Animated SVG semi-circular gauge
    │   │   └── ResultCard.jsx     # Verdict report, red flags, recommendations & report form
    │   ├── pages/
    │   │   ├── Scanner.jsx        # Main scanning dashboard page
    │   │   └── History.jsx        # Historical scans audit log with expandable details
    │   ├── api.js                 # Axios API service client
    │   ├── App.jsx                # Router & layout container
    │   ├── main.jsx               # React DOM root entry
    │   └── index.css              # Tailwind CSS styles
    ├── vite.config.js             # Vite configuration with API proxy
    ├── package.json               # Node.js dependencies
    └── index.html                 # Main HTML document
```

---

## 6. API Reference & Endpoints

Base URL: `http://localhost:8000` (or `http://localhost:5173/api` via Vite proxy)

### 1. Analyze URL
- **Endpoint**: `POST /api/analyze/url`
- **Body**:
```json
{
  "url": "http://paypal-security-update.xyz/login"
}
```
- **Response (200 OK)**:
```json
{
  "id": 1,
  "verdict": "Dangerous",
  "confidence": 89.9,
  "redFlags": [
    {
      "rule_id": "typosquatting",
      "description": "Domain contains 'paypal' but appears to be a deceptive imitation.",
      "severity": "high"
    },
    {
      "rule_id": "missing_https",
      "description": "Connection is not secure (missing HTTPS).",
      "severity": "low"
    },
    {
      "rule_id": "suspicious_tld",
      "description": "Domain uses a top-level domain frequently associated with spam.",
      "severity": "medium"
    }
  ],
  "explanation": "- Domain contains 'paypal' but appears to be a deceptive imitation.\n- Connection is not secure (missing HTTPS).",
  "recommendation": "Do not proceed. This is highly likely to be a threat.",
  "tips": [
    "Close the tab immediately.",
    "Do not download any files or run any scripts from this site.",
    "If you entered information, change your passwords and contact your bank if necessary."
  ]
}
```
- **Error Response (400 Bad Request)**:
```json
{
  "detail": "URL cannot be empty or whitespace only."
}
```

---

### 2. Analyze Email / SMS Text
- **Endpoint**: `POST /api/analyze/text`
- **Body**:
```json
{
  "text": "URGENT: Your account has been suspended. Click here to verify: http://bit.ly/bank-verify",
  "type": "email"
}
```
- **Response (200 OK)**:
```json
{
  "id": 2,
  "verdict": "Dangerous",
  "confidence": 94.6,
  "redFlags": [
    { "rule_id": "urgency_language", "description": "Contains urgency/pressure language.", "severity": "high" },
    { "rule_id": "threat_language", "description": "Contains threatening language.", "severity": "high" },
    { "rule_id": "url_shortener", "description": "URL uses a shortening service.", "severity": "medium" }
  ],
  "explanation": "- Contains urgency/pressure language.\n- URL uses a shortening service.",
  "recommendation": "Do not proceed. This is highly likely to be a threat.",
  "tips": [
    "Mark the email as spam and delete it.",
    "Do not reply to the sender or open any attachments.",
    "Never share OTPs, passwords, or personal details."
  ]
}
```

---

### 3. Analyze QR Code Image
- **Endpoint**: `POST /api/analyze/qr`
- **Form Data**: `file` (Image binary: PNG, JPG, WebP)
- **Response (200 OK)**:
```json
{
  "id": 3,
  "decoded_url": "http://phishing-update-account.tk/login",
  "verdict": "Dangerous",
  "confidence": 71.7,
  "redFlags": [
    { "rule_id": "missing_https", "description": "Connection is not secure.", "severity": "low" },
    { "rule_id": "suspicious_tld", "description": "Domain uses a suspicious TLD.", "severity": "medium" }
  ],
  "explanation": "- Connection is not secure (missing HTTPS).",
  "recommendation": "Do not proceed. This is highly likely to be a threat.",
  "tips": [ "Close the tab immediately.", "Do not download any files." ]
}
```

---

### 4. Fetch Scan History
- **Endpoint**: `GET /api/history`
- **Response (200 OK)**:
```json
[
  {
    "id": 3,
    "input_type": "qr",
    "input_value": "http://phishing-update-account.tk/login",
    "verdict": "Dangerous",
    "confidence": 71.7,
    "red_flags": "missing_https, suspicious_tld",
    "timestamp": "2026-08-28 10:35:12"
  }
]
```

---

### 5. Report Threat
- **Endpoint**: `POST /api/report`
- **Body**:
```json
{
  "scan_id": 3,
  "comment": "Confirmed malicious phishing page targeting student accounts."
}
```
- **Response (200 OK)**: `{"success": true}`

---

## 7. Installation & Setup Guide

### Prerequisites
- **Python 3.10+**
- **Node.js 18+** & **npm**

### Step 1: Backend Setup
```bash
cd backend

# 1. Install dependencies
pip install -r requirements.txt

# 2. Train the Machine Learning Model
python train_model.py

# 3. (Optional) Run Benchmark Suite
python benchmark_ml.py

# 4. Start the FastAPI Server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Step 2: Frontend Setup
```bash
cd frontend

# 1. Install Node dependencies
npm install

# 2. Start the Vite Development Server
npm run dev
```

Open **[http://localhost:5173](http://localhost:5173)** in your browser.

---

## 8. Machine Learning & Benchmarking

The ML model can be retrained or evaluated at any time:

### Training (`train_model.py`)
```bash
python backend/train_model.py
```
- Generates 3,684 clean, deduplicated, balanced training records across 8 attack categories and legitimate hard negatives.
- Multi-view feature extraction combining **Word-level TF-IDF (1–2 n-grams, 5,000 max features)** and **Char-level TF-IDF (3–5 n-grams, 12,000 max features)** via `FeatureUnion`.
- Fits balanced, regularized `LogisticRegression(C=3.0, class_weight='balanced', random_state=42)`.
- Validated with **5-Fold Stratified Cross-Validation** (99.95% accuracy, 1.0000 ROC-AUC).
- Serializes self-contained pipeline to `backend/models/phishing_model.pkl`.

### Benchmark Results (`benchmark_ml.py`)
```bash
python backend/benchmark_ml.py
```
```text
======================================================================
        CYBER SHIELD - ADVANCED ML BENCHMARK & EVALUATION
======================================================================
[1] Held-Out Test Split (20% Stratified Split from 3,684 Samples):
    - Total Test Samples: 737
    - Accuracy:           99.86%
    - Precision:          99.73%
    - Recall:             100.00%
    - F1-Score:           99.86%
    - ROC-AUC:            1.0000

    Confusion Matrix:
    [[TN: 368  FP:   1]
     [FN:   0  TP: 368]]

[2] Separate Real-World Validation Set (50 Hand-Curated Samples, Out-of-Sample):
    - Total Samples:      50 (25 Phishing, 25 Legitimate)
    - Real-World Acc:     96.00%
    - Real-World Prec:    96.00%
    - Real-World Recall:  96.00%
    - Real-World F1:      96.00%
    - Real-World ROC-AUC: 0.9856

    Confusion Matrix:
    [[TN: 24  FP:  1]
     [FN:  1  TP: 24]]

[3] Error Analysis (2 misclassifications out of 50 samples):
    - False Negative: "Your Uber ride receipt is ready. If you did not take this ride, dispute at http://uber-receipt-dispute.xyz"
      -> Reason: High proportion of benign receipt tokens masking malicious domain token.
    - False Positive: "Please verify your email address to complete registration on LinkedIn."
      -> Reason: Registration verification phrase contains keywords overlapping with phishing requests without full URL context.
======================================================================
```

---

## 9. Security & Optimization Features

1. **Sliding-Window IP Rate Limiter**:
   - Middleware intercepts incoming requests and tracks timestamps per client IP.
   - Default limit: 60 requests/minute (customizable via `RATE_LIMIT_PER_MINUTE`).
   - Automatically returns standard `X-RateLimit-Limit` and `X-RateLimit-Remaining` headers.
2. **CORS Security**:
   - Whitelist configurable via `ALLOWED_ORIGINS` environment variable.
   - Prevents unauthorized cross-origin scraping in production.
3. **SQLite WAL (Write-Ahead Logging)**:
   - High-throughput concurrency for simultaneous write and read requests without database locking.
4. **Input Sanitization & Normalization**:
   - URL prefixes (`http://`, `https://`) auto-normalized when missing.
   - Whitespace stripping and rejection of empty payloads with HTTP 400.

---

## 10. Automated Testing Suite

The repository contains an automated test suite ([`backend/test_suite.py`](file:///c:/Users/hp/Documents/cybershield/backend/test_suite.py)) with **28 unit and integration tests**:

```bash
python backend/test_suite.py
```

### Verified Test Cases:
- `test_empty_url_rejected_with_400`: Verifies empty URLs fail with HTTP 400.
- `test_whitespace_url_rejected_with_400`: Verifies whitespace URLs fail with HTTP 400.
- `test_arbitrary_word_rejected_with_400`: Verifies arbitrary non-URL words are rejected with HTTP 400.
- `test_text_with_spaces_rejected_in_url_tab`: Verifies general multi-word text submitted to URL endpoint is rejected with HTTP 400.
- `test_empty_text_rejected_with_400`: Verifies empty email/SMS text fails with HTTP 400.
- `test_safe_url`: Verifies legitimate URLs pass with 0 red flags.
- `test_typosquatting`: Verifies lookalike domains are detected as HIGH severity.
- `test_ip_based_url`: Verifies raw IP hosts are flagged.
- `test_at_sign_in_url`: Verifies `@` credential-hiding URLs are flagged.
- `test_excessive_subdomains`: Verifies nested subdomain tricks are flagged.
- `test_url_shortener`: Verifies URL shorteners (`bit.ly`, etc.) are detected.
- `test_data_uri`: Verifies data scheme payloads are flagged.
- `test_text_rules`: Verifies urgency, credential requests, and prize scam text rules.
- `test_legitimate_bank_otp_not_dangerous`: Verifies authentic bank OTP messages are classified safely.
- `test_legitimate_delivery_notification_safe`: Verifies legitimate parcel delivery notifications pass as safe.
- `test_legitimate_corporate_email_safe`: Verifies routine corporate emails pass as safe.
- `test_qr_standard_url_decode`: Verifies QR codes with standard web URLs decode and analyze accurately.
- `test_qr_non_url_text_decode`: Verifies QR codes containing plain non-URL text decode and analyze properly.
- `test_qr_invalid_image_raises_error`: Verifies invalid or unreadable image uploads return proper error responses.
- `test_safe_verdict` & `test_dangerous_verdict`: Verifies score combination and threshold mapping.
- `test_history_endpoint`: Verifies SQLite historical retrieval.
- `test_report_endpoint`: Verifies threat reporting submission.
- `test_rate_limit_headers`: Verifies rate limiting middleware headers.

**Result: 28 passed, 0 failed (100% Pass Rate).**

---

*Cyber Shield — HackSprint 2.0 © 2026*
