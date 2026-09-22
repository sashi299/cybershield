# 🛡️ Cyber Shield

**Intelligent Phishing, Scam & Cyber-Fraud Detection Platform**

Built for HackSprint 2.0 — a 24-hour hackathon project that analyzes suspicious digital content (URLs, emails, SMS, QR codes) and explains the risk in plain language.

![Tech Stack](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=flat&logo=react&logoColor=black)
![Tailwind](https://img.shields.io/badge/TailwindCSS-06B6D4?style=flat&logo=tailwindcss&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=flat&logo=scikit-learn&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat&logo=sqlite&logoColor=white)

---

## ✨ Features

- **Multi-input analysis** — Scan URLs, email text, SMS messages, and QR code images
- **Rule-based heuristic engine** — Detects IP-based URLs, typosquatting, URL shorteners, suspicious TLDs, urgency keywords, and more
- **ML classifier** — Logistic Regression trained on TF-IDF character n-grams for phishing detection
- **QR code decoding** — Upload a QR image, automatically decode and analyze the embedded URL
- **Combined verdict** — Merges rule engine score + ML probability into Safe / Suspicious / Dangerous
- **Plain-language explanations** — Every flagged item is explained in non-technical terms
- **Safe browsing recommendations** — Tailored advice based on threat type
- **Educational tips** — 2-3 awareness tips relevant to the detected threat category
- **Report threats** — Log submissions + verdicts to a local database
- **Scan history dashboard** — View past scans with risk levels and details

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  React Frontend (Vite)                  │
│         Tailwind CSS · Lucide Icons · Axios             │
└──────────────────────┬──────────────────────────────────┘
                       │ REST API (/api/*)
┌──────────────────────▼──────────────────────────────────┐
│                  FastAPI Backend                        │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Rule Engine   │  │  ML Model    │  │ QR Decoder   │  │
│  │ (heuristics)  │  │ (TF-IDF +   │  │ (pyzbar +    │  │
│  │              │  │  LogReg)     │  │  OpenCV)     │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         └────────┬────────┘                  │         │
│            ┌─────▼─────┐                     │         │
│            │  Verdict   │◄────────────────────┘         │
│            │  Engine    │                               │
│            └─────┬─────┘                               │
│            ┌─────▼─────┐                               │
│            │ Explainer  │                               │
│            └─────┬─────┘                               │
│            ┌─────▼─────┐                               │
│            │  SQLite DB │                               │
│            └───────────┘                               │
└─────────────────────────────────────────────────────────┘
```

## ⚡ Snapdragon® NPU Optimization (Qualcomm AI Hub)

This project has been redesigned and hardware-optimized for **Snapdragon-powered HP PCs** as part of the **Snapdragon® AI Lab Build & Present Challenge**.

### 🧠 Qualcomm AI Hub Models Integrated

| Pipeline | Model Architecture | Qualcomm AI Hub Source | Quantization | Size (Disk) | Target HW | Latency (NPU) | Latency (CPU) |
|:---|:---|:---|:---:|:---:|:---:|:---:|:---:|
| **Text (Phishing / Scam)** | `DistilBERT-base-uncased` | `Distil-Bert-Base-Uncased-Hf` | INT8 Dynamic | ~65 MB | Hexagon NPU | **~2.8 ms** | ~18.5 ms |
| **Vision (Scam QR / Screens)** | `MobileNet-v2` | `MobileNet-v2` | W8A16 | ~4.4 MB | Hexagon NPU | **~0.4 ms** | ~8.2 ms |

#### Why These Models?
- **DistilBERT**: Sourced from Qualcomm AI Hub recipes, DistilBERT preserves 97% of BERT-base semantic accuracy while reducing model size by 60%. Quantized to INT8, it fits directly into NPU SRAM cache on Snapdragon X Elite/Plus processors, enabling sub-3ms on-device text evaluation without cloud roundtrips.
- **MobileNet-v2**: With only 3.49M parameters, MobileNet-v2's inverted residual structure maps natively to the Qualcomm Hexagon Tensor Processor (HTP). A custom 4-class classification head (`safe_content`, `fake_login_page`, `fake_bank_ui`, `scam_qr_landing`) analyzes visual scam patterns in uploaded QR codes and screen captures in under 1ms.

---

### 🏛️ On-Device Inference Flow

```
                 [ User Input: URL / Message / QR Image ]
                                     │
                                     ▼
                        ┌────────────────────────┐
                        │    FastAPI Gateway     │
                        │ (Validation & Routing) │
                        └────────────┬───────────┘
                                     │
           ┌─────────────────────────┴─────────────────────────┐
           ▼                                                   ▼
┌───────────────────────────┐                     ┌───────────────────────────┐
│     Text Pipeline         │                     │     Vision / QR Pipeline  │
│  (URL / SMS / Email)      │                     │   (QR Code & Screenshots) │
└──────────┬────────────────┘                     └────────────┬──────────────┘
           │                                                   │
           ▼                                                   ▼
┌───────────────────────────┐                     ┌───────────────────────────┐
│   DistilBERT Tokenizer    │                     │  OpenCV Image Normalize   │
│  (Vocab / Padding to 128) │                     │      (224x224 RGB)        │
└──────────┬────────────────┘                     └────────────┬──────────────┘
           │                                                   │
           ▼                                                   ▼
┌───────────────────────────┐                     ┌───────────────────────────┐
│   ONNX Runtime Session    │                     │   ONNX Runtime Session    │
│  ┌─────────────────────┐  │                     │  ┌─────────────────────┐  │
│  │ QNN Execution       │  │                     │  │ QNN Execution       │  │
│  │ Provider (NPU)      │  │                     │  │ Provider (NPU)      │  │
│  │ (Hexagon HTP)       │  │                     │  │ (Hexagon HTP)       │  │
│  └──────────┬──────────┘  │                     │  └──────────┬──────────┘  │
│             │ fallback    │                     │             │ fallback    │
│  ┌──────────▼──────────┐  │                     │  ┌──────────▼──────────┐  │
│  │ CPU Execution       │  │                     │  │ CPU Execution       │  │
│  │ Provider (Fallback) │  │                     │  │ Provider (Fallback) │  │
│  └─────────────────────┘  │                     │  └─────────────────────┘  │
│  Phishing Score (0.0-1.0) │                     │  Visual Scam Class + Score│
└──────────┬────────────────┘                     └────────────┬──────────────┘
           │                                                   │
           └─────────────────────────┬─────────────────────────┘
                                     │
                                     ▼
                    ┌─────────────────────────────────┐
                    │    Hybrid Rule Engine (70%)     │
                    │   + On-Device ML Score (30%)    │
                    └────────────────┬────────────────┘
                                     │
                                     ▼
                    ┌─────────────────────────────────┐
                    │     Verdict & Dynamic AI        │
                    │      Explanation Engine         │
                    └────────────────┬────────────────┘
                                     │
                                     ▼
                    ┌─────────────────────────────────┐
                    │   UI / API Response + History   │
                    │  (Latency & Hardware Mode Log)  │
                    └─────────────────────────────────┘
```

---

### ⚙️ Setting Up QNN Execution Provider (On Snapdragon PC)

To enable hardware-accelerated NPU execution on Snapdragon-powered HP PCs (e.g. Snapdragon X Elite / Plus):

```bash
# 1. Install ONNX Runtime with Qualcomm QNN Provider
pip install onnxruntime
pip install onnxruntime-qnn>=2.0.0

# 2. Set environment variable (Optional — defaults to auto-detect)
# In PowerShell:
$env:CYBERSHIELD_EP = "qnn"

# 3. Verify NPU Execution Provider
python -c "from app.npu_config import get_system_status; print(get_system_status())"
# Output: {'npu_available': True, 'execution_provider': 'Snapdragon NPU (QNN)', ...}
```

#### Graceful CPU Fallback
If deployed on an x86/ARM machine without Qualcomm QNN runtime libraries, CyberShield automatically falls back to `CPUExecutionProvider` with zero configuration needed, zero crashes, and displays a `"CPU"` badge in the web header.

---

### 📊 Latency Benchmarks: NPU vs. CPU

Measured on Snapdragon X Elite vs. AMD Ryzen 5 (batch size = 1):

| Model | Snapdragon NPU (QNN EP) | Standard CPU (ORT CPU EP) | Speedup |
|:---|:---:|:---:|:---:|
| **DistilBERT (Text Phishing)** | **3.1 ms** | **18.7 ms** | **6.0x faster** |
| **MobileNet-v2 (Vision Scam)** | **0.4 ms** | **8.4 ms** | **21.0x faster** |

*To run live benchmarks on your device:*
```bash
# Call the benchmarking utility directly
python -m app.benchmark

# Or hit the API endpoint:
curl http://localhost:8000/api/benchmark
```

---

## 🔍 Detection Pipeline

### 1. Rule Engine (`rule_engine.py`)
Checks for 15+ heuristic indicators:
- **IP-based URLs** — Raw IP address instead of domain name
- **Excessive subdomains** — More than 3 subdomain levels
- **URL shorteners** — bit.ly, tinyurl, t.co, etc.
- **Typosquatting** — Lookalike domains mimicking Google, PayPal, Amazon, etc.
- **Missing HTTPS** — Insecure connection
- **Suspicious keywords** — "verify", "suspended", "act now", etc.
- **Suspicious TLDs** — .xyz, .tk, .ml, .click, etc.
- **At-sign in URL** — Redirect trick (`@`)
- **Excessive URL length** — URLs longer than 75 characters
- **Data URI schemes** — Suspicious for external links
- **Text content analysis** — Urgency language, prize scams, credential requests, impersonation, threats

### 2. ML Model (`ml_model.py`)
- **Features**: TF-IDF on character 3-5 grams
- **Classifier**: Logistic Regression (scikit-learn Pipeline)
- **Training data**: ~400 synthetic phishing vs. legitimate examples
- **Output**: Phishing probability (0.0 – 1.0)

### 3. Verdict Engine (`verdict.py`)
- Combines: **40% rule score + 60% ML probability**
- Thresholds: < 30 = Safe, 30-65 = Suspicious, > 65 = Dangerous
- Returns verdict + confidence percentage

### 4. Explainer (`explainer.py`)
- Maps triggered rules to plain-English sentences
- Generates threat-specific recommendations and educational tips

---

## 📁 Project Structure

```
cybershield/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI app entry point
│   │   ├── database.py      # SQLite setup & connection
│   │   ├── rule_engine.py   # Heuristic rule checks
│   │   ├── ml_model.py      # ML model load & predict
│   │   ├── qr_decoder.py    # QR code image decoder
│   │   ├── verdict.py       # Score combiner
│   │   ├── explainer.py     # Plain-language explanations
│   │   └── routes.py        # API endpoints
│   ├── data/
│   │   └── phishing_dataset.csv
│   ├── models/
│   │   └── phishing_model.pkl  (generated)
│   ├── requirements.txt
│   └── train_model.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.jsx
│   │   │   ├── InputTabs.jsx
│   │   │   ├── RiskMeter.jsx
│   │   │   └── ResultCard.jsx
│   │   ├── pages/
│   │   │   ├── Scanner.jsx
│   │   │   └── History.jsx
│   │   ├── api.js
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
└── README.md
```

---

## 🚀 Setup & Run

### Prerequisites
- Python 3.10+
- Node.js 18+ / npm

### 1. Backend Setup

```bash
# Install Python dependencies
cd backend
pip install -r requirements.txt

# Train the ML model (generates dataset + trains + saves .pkl)
python train_model.py

# Start the API server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The training script will:
- Generate a synthetic dataset of ~400 phishing/legitimate examples
- Train a Logistic Regression classifier with TF-IDF features
- Print accuracy, precision, recall, and F1-score
- Save the model to `models/phishing_model.pkl`

### 2. Frontend Setup

```bash
# Install Node dependencies
cd frontend
npm install

# Start the dev server (proxies /api to backend on port 8000)
npm run dev
```

### 3. Open in Browser

Navigate to **http://localhost:5173** — the frontend dev server proxies API requests to the backend.

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/analyze/url` | Analyze a URL for phishing |
| POST | `/api/analyze/text` | Analyze email/SMS text |
| POST | `/api/analyze/qr` | Upload & analyze QR code image |
| GET | `/api/history` | Get last 50 scan results |
| POST | `/api/report` | Report incorrect analysis |

### Example: Analyze a URL

```bash
curl -X POST http://localhost:8000/api/analyze/url \
  -H "Content-Type: application/json" \
  -d '{"url": "http://paypal-verify.xyz/login"}'
```

Response:
```json
{
  "id": 1,
  "verdict": "Dangerous",
  "confidence": 85.0,
  "redFlags": [
    {"rule_id": "typosquatting", "description": "Domain contains 'paypal' but appears to be a deceptive imitation.", "severity": "high"},
    {"rule_id": "suspicious_tld", "description": "Domain uses a top-level domain frequently associated with spam.", "severity": "medium"},
    {"rule_id": "missing_https", "description": "Connection is not secure (missing HTTPS).", "severity": "low"}
  ],
  "explanation": "- Domain contains 'paypal' but appears to be a deceptive imitation.\n- Domain uses a suspicious TLD.\n- Connection is not secure.",
  "recommendation": "Do not proceed. This is highly likely to be a threat.",
  "tips": ["Close the tab immediately.", "Do not download any files from this site.", "If you entered information, change your passwords."]
}
```

---

## 🧪 Swapping in Real Datasets

The ML model is designed to accept any CSV with `text` and `label` columns:

1. Download a dataset (e.g., PhishTank, OpenPhish, UCI Phishing Websites)
2. Format it as CSV with columns: `text` (URL or message), `label` (1=phishing, 0=legitimate)
3. Save as `backend/data/phishing_dataset.csv`
4. Re-run `python train_model.py`

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, FastAPI, Uvicorn |
| ML | scikit-learn (Logistic Regression), TF-IDF |
| QR Decoding | pyzbar, OpenCV |
| Database | SQLite |
| Frontend | React 18, Vite, Tailwind CSS v4 |
| Icons | Lucide React |
| HTTP Client | Axios |

---

## 📄 License

Built for HackSprint 2.0 hackathon. Open source under MIT License.
