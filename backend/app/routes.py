from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from pydantic import BaseModel
import re
from typing import Optional

from .rule_engine import analyze_url_rules, analyze_text_rules
from .ml_model import predict
from .qr_decoder import decode_qr
from .verdict import calculate_verdict
from .explainer import explain_rules, generate_recommendations
from .database import get_db_connection

router = APIRouter()

class URLRequest(BaseModel):
    url: str

class TextRequest(BaseModel):
    text: str
    type: str

class ReportRequest(BaseModel):
    scan_id: int
    comment: str

from urllib.parse import urlparse

def extract_urls(text: str) -> list:
    cleaned_urls = []
    seen_normalized = set()
    
    # 1. Extract explicit http/https links first
    explicit_matches = re.findall(r'https?://[^\s<>"\',)]+', text, re.IGNORECASE)
    for u in explicit_matches:
        clean = re.sub(r'[.,!?;:)>"\']+$', '', u).strip()
        if clean and len(clean) > 4:
            # Normalized without scheme for dedup
            norm = re.sub(r'^https?://', '', clean.lower())
            if norm not in seen_normalized:
                seen_normalized.add(norm)
                cleaned_urls.append(clean)

    # 2. Extract bare domains / shortener links (e.g. bit.ly/123, google.com)
    bare_matches = re.findall(r'\b(?:www\.[a-zA-Z0-9-]+\.[a-zA-Z]{2,}|[a-zA-Z0-9-]+\.[a-zA-Z]{2,})(?:/[^\s<>"\',)]*)?', text, re.IGNORECASE)
    for u in bare_matches:
        clean = re.sub(r'[.,!?;:)>"\']+$', '', u).strip()
        if not clean or len(clean) < 4:
            continue
        norm = re.sub(r'^https?://', '', clean.lower())
        if norm in seen_normalized:
            continue
            
        hostname = clean.split('/')[0].split('?')[0].lower()
        if _is_valid_tld(hostname):
            seen_normalized.add(norm)
            cleaned_urls.append('https://' + clean)
            
    return cleaned_urls

KNOWN_TLDS = {
    # Generic TLDs
    'com', 'org', 'net', 'edu', 'gov', 'mil', 'int',
    # Common TLDs
    'io', 'co', 'me', 'app', 'dev', 'ai', 'tech', 'site', 'online', 'store',
    'blog', 'cloud', 'digital', 'email', 'global', 'group', 'live', 'media',
    'network', 'news', 'one', 'page', 'plus', 'pro', 'shop', 'space', 'studio',
    'world', 'zone', 'web', 'wiki', 'tv', 'cc', 'biz', 'info', 'mobi', 'name',
    'tel', 'travel', 'jobs', 'cat', 'post', 'xxx', 'aero', 'asia', 'coop',
    'museum', 'academy', 'agency', 'business', 'company', 'consulting', 'design',
    'expert', 'finance', 'solutions', 'systems', 'tools', 'ventures', 'works',
    # Suspicious but real TLDs (used by scammers)
    'xyz', 'tk', 'ml', 'ga', 'cf', 'gq', 'top', 'buzz', 'club', 'work',
    'click', 'link', 'pw', 'icu', 'cyou', 'cfd', 'sbs', 'rest', 'fun',
    # Country code TLDs
    'us', 'uk', 'ca', 'au', 'de', 'fr', 'jp', 'cn', 'ru', 'br', 'in',
    'it', 'es', 'nl', 'se', 'no', 'dk', 'fi', 'pl', 'cz', 'sk', 'at',
    'ch', 'be', 'ie', 'pt', 'gr', 'hu', 'ro', 'bg', 'hr', 'si', 'lt',
    'lv', 'ee', 'mt', 'cy', 'lu', 'is', 'nz', 'za', 'mx', 'ar', 'cl',
    'co', 'pe', 've', 'ec', 'uy', 'py', 'bo', 'cr', 'pa', 'do', 'gt',
    'hn', 'sv', 'ni', 'cu', 'jm', 'tt', 'ky', 'sg', 'hk', 'tw', 'kr',
    'th', 'vn', 'ph', 'my', 'id', 'pk', 'bd', 'lk', 'np', 'mm', 'kh',
    'ae', 'sa', 'qa', 'kw', 'bh', 'om', 'jo', 'lb', 'il', 'eg', 'ma',
    'tn', 'dz', 'ng', 'ke', 'gh', 'tz', 'ug', 'et', 'cm', 'sn', 'ci',
    'ua', 'by', 'kz', 'ge', 'am', 'az', 'uz', 'kg', 'tj', 'tm', 'md',
    # Multi-part country TLDs
    'ac', 'ad', 'ag', 'al', 'an', 'ao', 'aq', 'as', 'aw', 'ax',
    'ba', 'bb', 'bf', 'bi', 'bj', 'bm', 'bn', 'bs', 'bt', 'bw',
    'bz', 'cd', 'cg', 'ck', 'cv', 'cw', 'cx', 'dj', 'dm', 'dz',
    'er', 'eu', 'fj', 'fk', 'fm', 'fo', 'gd', 'gi', 'gl', 'gm',
    'gn', 'gp', 'gu', 'gw', 'gy', 'hm', 'ht', 'im', 'iq', 'ir',
    'je', 'ki', 'km', 'kn', 'kp', 'la', 'lc', 'li', 'lr', 'ls',
    'ly', 'mc', 'mf', 'mg', 'mh', 'mk', 'mn', 'mo', 'mp', 'mq',
    'mr', 'ms', 'mu', 'mv', 'mw', 'mz', 'na', 'nc', 'ne', 'nf',
    'nr', 'nu', 'pf', 'pg', 'pm', 'pn', 'pr', 'ps', 'pw', 're',
    'rs', 'rw', 'sb', 'sc', 'sd', 'sh', 'sl', 'sm', 'sn', 'so',
    'sr', 'ss', 'st', 'su', 'sv', 'sx', 'sy', 'sz', 'tc', 'td',
    'tf', 'tg', 'tk', 'tl', 'to', 'tp', 'vc', 'vi', 'vg', 'vu',
    'wf', 'ws', 'ye', 'yt', 'zm', 'zw',
}

def _extract_tld(hostname: str) -> str:
    """Extract the TLD from a hostname, handling multi-part TLDs like co.uk."""
    parts = hostname.lower().split('.')
    if len(parts) < 2:
        return ''
    # Check 2-part TLDs first (e.g. co.uk, com.au, co.in)
    if len(parts) >= 3:
        two_part = f"{parts[-2]}.{parts[-1]}"
        common_two_part = {'co.uk', 'com.au', 'co.in', 'com.br', 'co.jp', 'co.kr',
                           'com.mx', 'com.cn', 'com.tw', 'com.sg', 'co.za', 'co.nz',
                           'com.ar', 'com.tr', 'co.id', 'com.my', 'com.ph', 'com.pk',
                           'com.ng', 'com.eg', 'com.sa', 'co.th', 'com.vn', 'com.ua',
                           'org.uk', 'net.au', 'ac.uk', 'gov.uk', 'edu.au', 'or.jp'}
        if two_part in common_two_part:
            return two_part
    return parts[-1]

def _is_valid_tld(hostname: str) -> bool:
    """Check if the hostname has a recognized real-world TLD."""
    tld = _extract_tld(hostname)
    if not tld:
        return False
    # For multi-part TLDs, check the last part
    last_part = tld.split('.')[-1] if '.' in tld else tld
    return last_part in KNOWN_TLDS

def validate_and_normalize_url(raw_url: str) -> str:
    url = raw_url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="URL cannot be empty or whitespace only.")
        
    if url.lower().startswith('data:'):
        return url
        
    # Check if user passed conversational text with spaces
    if ' ' in url:
        raise HTTPException(
            status_code=400, 
            detail="Invalid URL format: URLs cannot contain spaces. If you want to analyze message text, please switch to the Email or SMS tab."
        )

    # Normalize protocol if missing
    normalized_url = url
    if not url.lower().startswith(('http://', 'https://', 'ftp://')):
        # Check domain pattern before prepending http://
        ip_pattern = r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(?::[0-9]+)?(?:/.*)?$"
        domain_pattern = r"^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}(?::[0-9]+)?(?:/.*)?$"
        localhost_pattern = r"^localhost(?::[0-9]+)?(?:/.*)?$"
        
        if not (re.match(ip_pattern, url) or re.match(domain_pattern, url) or re.match(localhost_pattern, url, re.IGNORECASE)):
            raise HTTPException(
                status_code=400,
                detail=f"'{raw_url}' is not a valid website URL or domain name. Please enter a valid address (e.g. google.com, https://example.com) or use the Email/SMS tab."
            )
        normalized_url = 'https://' + url

    try:
        parsed = urlparse(normalized_url)
        netloc = parsed.netloc.split('@')[-1]  # handle @ in URL
        hostname = netloc.split(':')[0]  # strip port
        
        if not hostname:
            raise HTTPException(status_code=400, detail="Invalid URL: Domain or hostname is missing.")
            
        ip_match = re.match(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$", hostname)
        is_localhost = hostname.lower() == 'localhost'
        
        if ip_match or is_localhost:
            return normalized_url
        
        # Validate the TLD is a real, recognized TLD
        if not _is_valid_tld(hostname):
            tld = hostname.split('.')[-1] if '.' in hostname else hostname
            raise HTTPException(
                status_code=400, 
                detail=f"'{raw_url}' does not have a recognized domain extension (.{tld}). This does not appear to be a real website address."
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid URL structure: {str(e)}")

    return normalized_url

import socket

def _domain_resolves_dns(hostname: str) -> bool:
    try:
        socket.setdefaulttimeout(1.5)
        socket.gethostbyname(hostname)
        return True
    except Exception:
        return False

@router.post("/api/analyze/url")
def analyze_url(req: URLRequest):
    try:
        url = validate_and_normalize_url(req.url)
    except HTTPException as e:
        # Return a proper verdict result instead of HTTP 400 error
        detail_msg = e.detail if hasattr(e, 'detail') else str(e)
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO scans (input_type, input_value, verdict, confidence, red_flags, explanation, recommendation, tips)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', ("url", req.url, "Safe", 0.0, "invalid_url",
                  detail_msg,
                  "The entered URL is not valid. Please check the address and try again.",
                  "- Check spelling of the domain name.\n- Make sure to include the full URL.\n- Use the Text/SMS tab for non-URL content."))
            conn.commit()
            scan_id = cursor.lastrowid
        return {
            "id": scan_id,
            "verdict": "Safe",
            "confidence": 0.0,
            "redFlags": [{
                "rule_id": "invalid_url",
                "description": detail_msg,
                "severity": "info"
            }],
            "explanation": detail_msg,
            "recommendation": "The entered URL is not valid. Please check the address and try again.",
            "tips": ["Check spelling of the domain name.", "Make sure to include the full URL.", "Use the Text/SMS tab for non-URL content."]
        }
    rule_results = analyze_url_rules(url)
    ml_prob = predict(url)
    
    parsed = urlparse(url)
    hostname = parsed.netloc.split('@')[-1].split(':')[0].lower()
    is_ip = bool(re.match(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$", hostname))
    is_localhost = hostname == 'localhost'
    
    # Check if domain resolves on the internet
    if not is_ip and not is_localhost:
        resolves = _domain_resolves_dns(hostname)
        if not resolves:
            if rule_results["score"] == 0:
                # Non-existent domain — return a proper result instead of 400 error
                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO scans (input_type, input_value, verdict, confidence, red_flags, explanation, recommendation, tips)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', ("url", url, "Safe", 70.0, "inactive_domain", 
                          f"'{req.url}' does not appear to be an active or registered website (DNS lookup failed). This domain is not currently reachable on the internet.",
                          "This domain is not active. It cannot harm you right now, but be cautious if you received this link from someone.",
                          "- Verify the spelling of the domain name.\n- Do not enter credentials on unreachable websites.\n- The domain may be expired, parked, or not yet registered."))
                    conn.commit()
                    scan_id = cursor.lastrowid
                return {
                    "id": scan_id,
                    "verdict": "Safe",
                    "confidence": 70.0,
                    "redFlags": [{
                        "rule_id": "inactive_domain",
                        "description": f"'{req.url}' is not an active website. DNS lookup failed — the domain is unreachable, expired, or not registered.",
                        "severity": "info"
                    }],
                    "explanation": f"'{req.url}' does not appear to be an active or registered website (DNS lookup failed). This domain is not currently reachable on the internet.",
                    "recommendation": "This domain is not active. It cannot harm you right now, but be cautious if you received this link from someone.",
                    "tips": ["Verify the spelling of the domain name.", "Do not enter credentials on unreachable websites.", "The domain may be expired, parked, or not yet registered."]
                }
            else:
                # Phishing simulation or sinkholed malicious domain
                rule_results["triggered_rules"].append({
                    "rule_id": "inactive_or_sinkholed",
                    "description": "Domain does not currently resolve via live DNS (unregistered, offline, or blocked by security providers).",
                    "severity": "medium"
                })
                rule_results["score"] = max(rule_results["score"], 50)
    
    verdict_data = calculate_verdict(rule_results["score"], ml_prob)
    explanation = explain_rules(rule_results["triggered_rules"], input_type="url", input_text=url)
    recommendation, tips = generate_recommendations(verdict_data["verdict"], "phishing URL", input_text=url)
    
    red_flags = ", ".join([r["rule_id"] for r in rule_results["triggered_rules"]])
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO scans (input_type, input_value, verdict, confidence, red_flags, explanation, recommendation, tips)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', ("url", url, verdict_data["verdict"], verdict_data["confidence"], red_flags, explanation, recommendation, tips))
        conn.commit()
        scan_id = cursor.lastrowid
        
    return {
        "id": scan_id,
        "verdict": verdict_data["verdict"],
        "confidence": verdict_data["confidence"],
        "redFlags": rule_results["triggered_rules"],
        "explanation": explanation,
        "recommendation": recommendation,
        "tips": [t.strip().lstrip("- ") for t in tips.split("\n") if t.strip()]
    }

@router.post("/api/analyze/text")
def analyze_text(req: TextRequest):
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="Text content cannot be empty or whitespace only.")
        
    text = req.text.strip()
    threat_type = "email scam" if req.type == "email" else "SMS smishing" if req.type == "sms" else "general"
    
    extracted_urls = extract_urls(text)
    
    max_rule_score = 0
    all_triggered_rules = []
    
    ml_scores = [predict(text)]
    
    # Analyze text content for phishing keywords
    text_rules = analyze_text_rules(text)
    if text_rules["score"] > max_rule_score:
        max_rule_score = text_rules["score"]
    all_triggered_rules.extend(text_rules["triggered_rules"])
    
    # Analyze any extracted URLs
    for url in extracted_urls:
        res = analyze_url_rules(url)
        if res["score"] > max_rule_score:
            max_rule_score = max(max_rule_score, res["score"])
        for r in res["triggered_rules"]:
            flag = {
                "rule_id": f"link_{r['rule_id']}",
                "description": f"Embedded Link ({url}): {r['description']}",
                "severity": r["severity"]
            }
            all_triggered_rules.append(flag)
        ml_scores.append(predict(url))
        
    ml_prob = max(ml_scores)
    
    verdict_data = calculate_verdict(max_rule_score, ml_prob)
    explanation = explain_rules(all_triggered_rules, input_type="text", input_text=text)
    recommendation, tips = generate_recommendations(verdict_data["verdict"], threat_type, input_text=text)
    
    red_flags = ", ".join([r["rule_id"] for r in all_triggered_rules])
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO scans (input_type, input_value, verdict, confidence, red_flags, explanation, recommendation, tips)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', ("text", text, verdict_data["verdict"], verdict_data["confidence"], red_flags, explanation, recommendation, tips))
        conn.commit()
        scan_id = cursor.lastrowid
        
    return {
        "id": scan_id,
        "verdict": verdict_data["verdict"],
        "confidence": verdict_data["confidence"],
        "redFlags": all_triggered_rules,
        "explanation": explanation,
        "recommendation": recommendation,
        "tips": [t.strip().lstrip("- ") for t in tips.split("\n") if t.strip()]
    }

@router.post("/api/analyze/qr")
def analyze_qr(file: UploadFile = File(...)):
    try:
        contents = file.file.read()
        decoded_content = decode_qr(contents)
    except Exception as e:
        # Return a proper result instead of 400 error
        error_msg = str(e)
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO scans (input_type, input_value, verdict, confidence, red_flags, explanation, recommendation, tips)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', ("qr", "invalid_qr", "Safe", 0.0, "invalid_qr",
                  f"Could not decode QR code: {error_msg}. The image may not contain a valid QR code.",
                  "The uploaded image does not contain a readable QR code. Try scanning a clearer image.",
                  "- Make sure the image contains a QR code.\n- Ensure the QR code is clearly visible and not blurry.\n- Try taking a new photo with better lighting."))
            conn.commit()
            scan_id = cursor.lastrowid
        return {
            "id": scan_id,
            "decoded_url": "",
            "verdict": "Safe",
            "confidence": 0.0,
            "redFlags": [{
                "rule_id": "invalid_qr",
                "description": f"Could not decode QR code: {error_msg}",
                "severity": "info"
            }],
            "explanation": f"Could not decode QR code: {error_msg}. The image may not contain a valid QR code.",
            "recommendation": "The uploaded image does not contain a readable QR code. Try scanning a clearer image.",
            "tips": ["Make sure the image contains a QR code.", "Ensure the QR code is clearly visible and not blurry.", "Try taking a new photo with better lighting."]
        }
    
    cleaned = decoded_content.strip()
    is_url = cleaned.lower().startswith(('http://', 'https://', 'www.')) or ('.' in cleaned and ' ' not in cleaned and len(cleaned.split('.')) >= 2)
    
    if is_url:
        rule_results = analyze_url_rules(cleaned)
        ml_prob = predict(cleaned)
        verdict_data = calculate_verdict(rule_results["score"], ml_prob)
        explanation = explain_rules(rule_results["triggered_rules"], input_type="url", input_text=cleaned)
        recommendation, tips = generate_recommendations(verdict_data["verdict"], "phishing URL", input_text=cleaned)
    else:
        rule_results = analyze_text_rules(cleaned)
        ml_prob = predict(cleaned)
        verdict_data = calculate_verdict(rule_results["score"], ml_prob)
        explanation = explain_rules(rule_results["triggered_rules"], input_type="text", input_text=cleaned)
        recommendation, tips = generate_recommendations(verdict_data["verdict"], "general", input_text=cleaned)
    
    red_flags = ", ".join([r["rule_id"] for r in rule_results["triggered_rules"]])
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO scans (input_type, input_value, verdict, confidence, red_flags, explanation, recommendation, tips)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', ("qr", cleaned, verdict_data["verdict"], verdict_data["confidence"], red_flags, explanation, recommendation, tips))
        conn.commit()
        scan_id = cursor.lastrowid
        
    return {
        "id": scan_id,
        "decoded_url": cleaned,
        "verdict": verdict_data["verdict"],
        "confidence": verdict_data["confidence"],
        "redFlags": rule_results["triggered_rules"],
        "explanation": explanation,
        "recommendation": recommendation,
        "tips": [t.strip().lstrip("- ") for t in tips.split("\n") if t.strip()]
    }

@router.get("/api/history")
def get_history():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM scans ORDER BY timestamp DESC LIMIT 50')
        rows = cursor.fetchall()
        results = []
        for row in rows:
            row_dict = dict(row)
            # Transform red_flags string -> redFlags list of objects
            red_flags_str = row_dict.get("red_flags", "") or ""
            red_flags_list = []
            for rf in red_flags_str.split(", "):
                rf = rf.strip()
                if rf:
                    red_flags_list.append({
                        "rule_id": rf,
                        "description": rf.replace("_", " ").title(),
                        "severity": "medium"
                    })
            # Transform tips string -> tips list of strings
            tips_str = row_dict.get("tips", "") or ""
            tips_list = [t.strip().lstrip("- ") for t in tips_str.split("\n") if t.strip()]
            
            results.append({
                "id": row_dict.get("id"),
                "verdict": row_dict.get("verdict", "Safe"),
                "confidence": row_dict.get("confidence", 0.0),
                "redFlags": red_flags_list,
                "explanation": row_dict.get("explanation", ""),
                "recommendation": row_dict.get("recommendation", ""),
                "tips": tips_list,
                "target": row_dict.get("input_value", ""),
                "input_type": row_dict.get("input_type", ""),
                "timestamp": row_dict.get("timestamp", ""),
            })
        return results

@router.post("/api/report")
def report_scan(req: ReportRequest):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO reports (scan_id, user_comment) VALUES (?, ?)', (req.scan_id, req.comment))
        conn.commit()
    return {"success": True}
