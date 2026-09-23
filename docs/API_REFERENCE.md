# ⚙️ CyberShield — Backend Technical Documentation

> **Intelligent Phishing & Fraud Detection Engine — Server, ML & API Architecture**
> **Tech Stack:** Python 3.10+, FastAPI, Uvicorn, SQLite (WAL mode), scikit-learn 1.9.0, PyZbar, OpenCV

---

## 📋 Table of Contents
1. [Overview & System Architecture](#1-overview--system-architecture)
2. [Project Directory Structure](#2-project-directory-structure)
3. [Core Modules & Pipeline Flow](#3-core-modules--pipeline-flow)
4. [Heuristic Rule Engine](#4-heuristic-rule-engine)
5. [Machine Learning Subsystem](#5-machine-learning-subsystem)
6. [QR Code Decoder & Computer Vision](#6-qr-code-decoder--computer-vision)
7. [Verdict & Confidence Engine](#7-verdict--confidence-engine)
8. [Database Architecture (SQLite WAL)](#8-database-architecture-sqlite-wal)
9. [Security, Middleware & Rate Limiting](#9-security-middleware--rate-limiting)
10. [REST API Endpoint Specifications](#10-rest-api-endpoint-specifications)
11. [Testing & Quality Assurance (28 Tests)](#11-testing--quality-assurance-28-tests)
12. [Setup, Training & Running Guide](#12-setup-training--running-guide)

---

## 1. Overview & System Architecture

CyberShield Backend is a high-performance Python/FastAPI microservice designed to analyze arbitrary URLs, emails, SMS text, and QR code images to detect phishing, spoofing, and fraud in milliseconds.

It employs a **hybrid detection architecture**:
1. **Deterministic Heuristic Rules Engine**: Evaluates domain structures, typosquatting, shorteners, IPv4 hosts, suspicious TLDs, and text urgency.
2. **Machine Learning Classifier**: Multi-view TF-IDF (Word + Character n-grams) Logistic Regression pipeline trained on 3,684 diverse real-world samples.
3. **Computer Vision QR Decoder**: Multi-stage QR decoding utilizing PyZbar with OpenCV adaptive threshold fallback.
4. **Weighted Ensemble Verdict Engine**: Merges deterministic rule weights and ML probabilistic confidence into calibrated risk ratings.

---

## 2. Project Directory Structure

`	ext
backend/
├── requirements.txt           # Pinned Python dependencies
├── train_model.py             # Dataset generation, 5-Fold CV & model training pipeline
├── benchmark_ml.py            # Held-out & out-of-sample benchmarking with error analysis
├── test_suite.py              # Automated test suite (28 unit & integration tests)
├── generate_test_qr.py        # Script to generate varied QR test fixture images
├── data/
│   ├── phishing_dataset.csv   # Full balanced dataset (3,684 samples)
│   └── test_set.csv           # Held-out test partition (737 samples)
├── models/
│   └── phishing_model.pkl     # Serialized multi-view FeatureUnion ML pipeline
├── test_qr_images/            # Test QR image suite (standard, small, low-contrast, no_qr)
└── app/
    ├── __init__.py            # App package initializer
    ├── main.py                # FastAPI app creation, CORS, and RateLimiter registration
    ├── routes.py              # REST API route handlers (/api/analyze/*, /api/history, /api/report)
    ├── rule_engine.py         # Heuristic rules for URLs and text (with safe context filters)
    ├── ml_model.py            # Runtime model loader and probability inference helper
    ├── verdict.py             # Decision engine combining rule weights and ML scores
    ├── explainer.py           # Natural language explanation and safety advice generator
    ├── qr_decoder.py          # PyZbar and OpenCV image preprocessing for QR decoding
    ├── rate_limiter.py        # Sliding-window in-memory rate limiter with stale key cleanup
    └── database.py            # SQLite schema initialization and connection context manager
`

---

## 3. Core Modules & Pipeline Flow

| File | Purpose | Key Functions / Classes |
| :--- | :--- | :--- |
| pp/main.py | FastAPI application factory | pp, lifespan startup handler |
| pp/routes.py | API endpoints & validation | nalyze_url(), nalyze_text(), nalyze_qr(), alidate_and_normalize_url(), extract_urls() |
| pp/rule_engine.py | Deterministic threat rules | nalyze_url_rules(), nalyze_text_rules() |
| pp/ml_model.py | Inference pipeline interface | load_model(), predict() |
| pp/verdict.py | Risk score arbitration | calculate_verdict(rule_score, ml_prob) |
| pp/explainer.py | Natural language explanation | explain_rules(), generate_recommendations() |
| pp/qr_decoder.py | Computer vision QR reader | decode_qr(image_bytes) |
| pp/rate_limiter.py | DDoS / spam mitigation | RateLimitMiddleware |
| pp/database.py | Persistence layer | get_db_connection(), init_db() |

---

## 4. Heuristic Rule Engine (pp/rule_engine.py)

### A. URL Heuristics (nalyze_url_rules)
- **IP-Based Host (ip_based, weight: +60)**: Detects raw IP addresses instead of domains (e.g. http://192.168.1.1/login).
- **Typosquatting & Brand Spoofing (	yposquatting, weight: +70)**: Detects deceptive brand lookalikes for popular targets (PayPal, Google, Amazon, Microsoft, Apple, Netflix, Chase, etc.).
- **URL Shortener (url_shortener, weight: +35)**: Flags redirection shorteners (it.ly, 	inyurl.com, 	.co, is.gd, etc.).
- **Suspicious TLDs (suspicious_tld, weight: +45)**: Checks for high-abuse TLDs (.xyz, .tk, .top, .buzz, .club, .click, .pw, etc.).
- **Missing HTTPS (missing_https, weight: +20)**: Flags unencrypted HTTP connections.
- **Embedded @ Symbol (t_sign, weight: +65)**: Detects URL credentials hiding the real destination.
- **Excessive Subdomains (excessive_subdomains, weight: +40)**: Flags domains with >4 subdomain levels.
- **Data URI Scheme (data_uri, weight: +80)**: Flags inline executable scripts.

### B. Text Heuristics & Safe Context Filters (nalyze_text_rules)
- **Safe Context Allowlist**: Recognizes authentic 2FA/OTP patterns (
'your otp (?:is|for)\s*[:\s]*\d{4,8}'), anti-fraud warnings, and order tracking numbers.
- When safe context is present, urgency and benign OTP mentions are suppressed to prevent false positives on legitimate banking or shipping alerts.
- When combined threat signals (Urgency + Credential Request + Suspicious URL) co-occur, a combined_phishing_signals rule (+50 weight) triggers.

---

## 5. Machine Learning Subsystem (	rain_model.py & pp/ml_model.py)

### A. Dataset (3,684 Samples)
- **1,842 Phishing Samples**: Banking, Delivery, Tech, Crypto, Lottery, and Obfuscated URLs.
- **1,842 Legitimate Samples**: Real 2FA OTPs, real delivery tracking with order #s, corporate urgency messages, billing receipts, and developer documentation.

### B. Feature Extraction Pipeline
- Combined **Word-level TF-IDF (1–2 n-grams, 5,000 max features)** and **Char-level TF-IDF (3–5 n-grams, 12,000 max features)** via FeatureUnion.

### C. Validation & Benchmarks
- **5-Fold Stratified Cross-Validation**: **99.95% Accuracy**, **1.0000 ROC-AUC**.
- **Held-Out Test Set (737 samples)**: **99.86% Accuracy**, **99.73% Precision**, **100.00% Recall**.
- **Out-of-Sample Real-World Validation (50 Hand-Curated Samples)**: **96.00% Accuracy**, **0.9856 ROC-AUC**.

---

## 6. QR Code Decoder (pp/qr_decoder.py)

The QR reader handles clean and degraded images through a two-stage process:
1. **Stage 1 (Primary)**: Uses PIL.Image + pyzbar.decode(). Fast path for standard QR codes.
2. **Stage 2 (Fallback)**: If Stage 1 fails, converts raw image buffer to an OpenCV matrix (cv2.imdecode), converts to grayscale (cv2.COLOR_BGR2GRAY), applies **Otsu Adaptive Thresholding** (cv2.THRESH_OTSU), and retries decoding.
3. If no QR code exists, raises ValueError('No QR code found in the image').

---

## 7. Verdict & Confidence Engine (pp/verdict.py)

Combines rule weights and ML predicted probabilities into an arbitrated verdict:
\text{Combined Score} = (0.55 \times \text{Rule Score}) + (0.45 \times \text{ML Probability} \times 100)

- **Score < 40**: 🟢 **Safe**
- **40 <= Score <= 69**: 🟡 **Suspicious**
- **Score >= 70**: 🔴 **Dangerous**

---

## 8. Database Architecture (pp/database.py)

SQLite database (cybershield.db) operates with **WAL (Write-Ahead Logging)** mode for high concurrency.

- **scans Table**: Stores scan ID, input type, input value, verdict, confidence, red flags, explanation, recommendation, tips, and timestamp.
- **	hreat_reports Table**: Stores user threat feedback and false positive reports.

---

## 9. Security, Middleware & Rate Limiting

1. **Sliding-Window Rate Limiter (pp/rate_limiter.py)**: 60 req/min per IP with stale entry deletion and 10,000 max-tracked-IP safeguard.
2. **CORS Whitelist**: Configurable via ALLOWED_ORIGINS env variable.
3. **Strict URL Normalization**: Validates hostnames against ~200 real ICANN TLDs (KNOWN_TLDS).

---

## 10. REST API Endpoint Specifications

- **POST /api/analyze/url**: Analyzes URL for phishing indicators.
- **POST /api/analyze/text**: Analyzes Email/SMS text and all extracted embedded links.
- **POST /api/analyze/qr**: Decodes and analyzes QR code image.
- **GET /api/history**: Retrieves scan audit history.
- **POST /api/report**: Submits user feedback / false positive report.

---

## 11. Testing & Quality Assurance (28 Tests)

`ash
python test_suite.py
`
- **28 / 28 Tests Passing** covering Rules, False Positives, QR Decoding, Verdict Engine, and API Endpoints.

---

## 12. Setup, Training & Running Guide

`ash
cd backend
pip install -r requirements.txt
python train_model.py
python benchmark_ml.py
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
`
API Documentation at **http://127.0.0.1:8000/docs**.
