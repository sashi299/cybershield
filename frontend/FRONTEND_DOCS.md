# 🛡️ CyberShield — Frontend Technical Documentation

> **Intelligent Phishing & Fraud Detection Engine — UI & Client Architecture**  
> **Tech Stack:** React 18, Vite 6, Tailwind CSS v4, Lucide Icons, Fetch API

---

## 📋 Table of Contents
1. [Overview & Features](#1-overview--features)
2. [Project Directory Structure](#2-project-directory-structure)
3. [Component Hierarchy & Architecture](#3-component-hierarchy--architecture)
4. [Component Deep Dive](#4-component-deep-dive)
5. [State Management & Data Flow](#5-state-management--data-flow)
6. [API Integration Layer](#6-api-integration-layer)
7. [Design System & UI Theme](#7-design-system--ui-theme)
8. [Setup & Running Guide](#8-setup--running-guide)
9. [Build & Deployment Guide](#9-build--deployment-guide)

---

## 1. Overview & Features

CyberShield Frontend is a single-page application (SPA) built for real-time security threat analysis. It provides an intuitive, high-contrast dark cybersecurity dashboard with:

- **Multi-Input Scanning Tabs**: Seamless switching between **URL**, **Email Text**, **SMS Message**, and **QR Code Image Upload**.
- **Interactive Risk Meter**: SVG gauge meter rendering real-time risk classification (**Safe**, **Suspicious**, **Dangerous**) with animated confidence percentages.
- **Explainable AI Breakdown**: Expandable red flags, threat descriptions, severity badges, actionable safety recommendations, and security tips.
- **Threat Reporting System**: Direct feedback mechanism allowing users to submit false-positive or confirmed threat reports.
- **Historical Scan Log**: Dedicated view of all previous scans with filtering, confidence ratings, timestamps, and deep-dive modal views.
- **Client-Side Validation & Feedback**: Inline error banners with clear corrective guidance (e.g. invalid domain extensions, empty fields).

---

## 2. Project Directory Structure

`	ext
frontend/
├── index.html                 # Main HTML template (dark background, responsive viewport)
├── package.json               # Dependencies & scripts (React 18, Vite 6, Tailwind v4)
├── vite.config.js             # Vite configuration with /api backend proxy (port 8000)
├── public/                    # Static assets & icons
└── src/
    ├── main.jsx               # React DOM entry point & root renderer
    ├── App.jsx                # Top-level shell with Header, Navigation & Page Router
    ├── index.css              # Global styles, Tailwind imports, and dark theme variables
    ├── api.js                 # Unified API client for backend communication
    ├── pages/
    │   ├── Scanner.jsx        # Main scanning dashboard page
    │   └── History.jsx        # Scan audit log & history table page
    └── components/
        ├── Header.jsx         # App navigation bar with live status badge & page switcher
        ├── InputTabs.jsx      # Multi-modal input tabs (URL, Email, SMS, QR upload)
        ├── RiskMeter.jsx      # Visual SVG gauge meter for threat scores
        ├── ResultCard.jsx     # Analysis card with Red Flags, Explanations, and Tips
        └── Footer.jsx         # Hackathon footer with live engine specs & status
`

---

## 3. Component Hierarchy & Architecture

`mermaid
graph TD
    App[App.jsx - Root State & Router] --> Header[Header.jsx - Navbar & Active Page]
    App --> Scanner[pages/Scanner.jsx]
    App --> History[pages/History.jsx]
    App --> Footer[Footer.jsx]

    Scanner --> InputTabs[InputTabs.jsx - URL / Email / SMS / QR]
    Scanner --> ResultCard[ResultCard.jsx - Detailed Analysis]
    ResultCard --> RiskMeter[RiskMeter.jsx - SVG Threat Gauge]
    ResultCard --> ReportModal[Threat Reporting Modal]

    History --> HistoryTable[Scan History List & Modal Viewer]
    
    InputTabs --> API[api.js]
    History --> API
    ResultCard --> API
`

---

## 4. Component Deep Dive

### 1. src/App.jsx
- Manages top-level active tab navigation (scanner vs history).
- Houses the main layout container with gradient background glow effects.
- Renders Header, active page, and Footer.

### 2. src/pages/Scanner.jsx
- Orchestrates the full scanning workflow.
- **States**: 
esult (analysis payload), loading (spinner flag), error (validation/network error text).
- Manages scan transitions and auto-scrolls to results upon receiving analysis.

### 3. src/components/InputTabs.jsx
- Multi-channel input interface with 4 dedicated tabs:
  - **URL Tab**: Single-line text input with auto-trimming and protocol validation.
  - **Email Tab**: Multi-line textarea for analyzing full email headers and body.
  - **SMS Tab**: Multi-line textarea for short message smishing detection.
  - **QR Code Tab**: Drag-and-drop / file upload zone for decoding QR images (.png, .jpg, .jpeg).
- Dispatches requests to src/api.js and formats user-friendly error banners.

### 4. src/components/RiskMeter.jsx
- Circular SVG arc gauge visualizing risk from 0% to 100%.
- Dynamic color thresholds:
  - 🟢 **Safe** (#10B981): Score < 40%
  - 🟡 **Suspicious** (#F59E0B): Score 40% – 69%
  - 🔴 **Dangerous** (#EF4444): Score $\ge$ 70%
- Formats confidence values to 1 decimal place (.toFixed(1)).

### 5. src/components/ResultCard.jsx
- Displays the complete forensic breakdown:
  - **Verdict Banner**: Color-coded risk status badge.
  - **Red Flags List**: Badges with rule IDs, severities (low, medium, high), and forensic descriptions.
  - **Analysis Explanation**: Plain-language reasoning explaining why the input was flagged.
  - **Actionable Recommendation**: Immediate defensive instructions.
  - **Security Tips**: Expandable accordion with preventative cybersecurity best practices.
  - **Report Button**: Opens modal to flag false positives or report confirmed threats.

### 6. src/pages/History.jsx
- Retrieves and displays scan history from GET /api/history.
- Displays tabular view with input type icon, target preview, verdict badge, confidence score, and timestamp.
- Includes search/filter and detailed modal view.

---

## 5. State Management & Data Flow

Data flows cleanly from top-level page components down to presentational components via React props:

1. **User Action**: User types URL/message or uploads QR image in InputTabs.jsx.
2. **API Call**: InputTabs invokes scanUrl(), scanText(), or scanQR() from pi.js.
3. **State Update**: Result payload is passed up to Scanner.jsx via onScanComplete(data).
4. **Rendering**: Scanner.jsx passes 
esult into ResultCard.jsx, which renders RiskMeter.jsx and detailed flags.
5. **Persistence**: Scan is automatically recorded in SQLite by backend and becomes visible in History.jsx.

---

## 6. API Integration Layer (src/api.js)

All network requests are centralized in src/api.js using standard Fetch API:

`javascript
// Scan URL
export const scanUrl = async (url) => {
  const res = await fetch('/api/analyze/url', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url })
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Failed to scan URL');
  }
  return res.json();
};

// Scan Email / SMS Text
export const scanText = async (text, type = 'email') => {
  const res = await fetch('/api/analyze/text', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, type })
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Failed to scan text');
  }
  return res.json();
};

// Scan QR Code Image
export const scanQR = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch('/api/analyze/qr', {
    method: 'POST',
    body: formData
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Failed to decode QR code');
  }
  return res.json();
};

// Fetch History
export const fetchHistory = async () => {
  const res = await fetch('/api/history');
  return res.json();
};

// Submit Threat Report
export const submitReport = async (scanId, comment) => {
  const res = await fetch('/api/report', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ scan_id: scanId, comment })
  });
  return res.json();
};
`

---

## 7. Design System & UI Theme

- **Background**: Slate dark theme (#0B1120, #111827, #1E293B).
- **Accents**: Neon Cyan (#06B6D4), Emerald Green (#10B981), Amber (#F59E0B), Rose Red (#EF4444).
- **Typography**: Inter / System UI sans-serif with monospace font for hashes, URLs, and code snippets.
- **Glassmorphism**: Backdrop blur with semi-transparent border strokes (order-slate-800/80 bg-slate-900/60 backdrop-blur-md).

---

## 8. Setup & Running Guide

### Prerequisites
- **Node.js**: v18.0.0 or later (v20+ recommended)
- **npm**: v9.0.0 or later

### Installation
`ash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install
`

### Running Local Development Server
`ash
npm run dev
`
- App will start at **http://localhost:5173** (or http://127.0.0.1:5173).
- Vite automatically proxies /api/* requests to the backend server at http://127.0.0.1:8000.

---

## 9. Build & Deployment Guide

`ash
# Generate optimized production build
npm run build

# Preview production build locally
npm run preview
`
- The production bundle is output to rontend/dist/ ready to be served by Nginx, Vercel, Netlify, or FastAPI static mounting.
