import re
from urllib.parse import urlparse

def explain_rules(triggered_rules: list, input_type: str = "url", input_text: str = "") -> str:
    text_lower = input_text.lower() if input_text else ""
    
    # 1. When no red flags are triggered (Safe)
    if not triggered_rules:
        if input_type == "url":
            try:
                parsed = urlparse(input_text if "://" in input_text else f"https://{input_text}")
                host = parsed.netloc or input_text
                return f"Verified clean domain structure for '{host}'. The URL uses standard secure web protocols, contains no typosquatting imitations, no deceptive subdomains, and has a legitimate security profile."
            except Exception:
                return "Legitimate domain structure. Standard protocol and registered domain verified with no typosquatting, blacklisted TLDs, IP hostnames, or deceptive patterns detected."
        elif input_type in ("email", "sms", "text"):
            if any(k in text_lower for k in ["otp", "verification code", "one time password"]):
                return "Legitimate transactional OTP / notification format. The message includes standard security guidance and does not attempt to redirect you to deceptive credential-harvesting links."
            elif any(k in text_lower for k in ["order", "shipped", "delivered", "tracking", "package"]):
                return "Genuine shipping / service update. No phishing links, urgency coercion, or suspicious requests for sensitive personal details detected."
            else:
                return "Normal conversational text. Analysis found no psychological manipulation, fake urgency, lottery claims, financial requests, or malicious redirect links."
        return "No suspicious patterns or threat indicators were detected."

    # 2. Dynamic, context-specific threat breakdown for triggered rules
    explanations = []
    
    # Category detection
    has_banking = any("bank" in r.get("description", "").lower() or "financial" in r.get("description", "").lower() or r.get("rule_id") == "financial_request" for r in triggered_rules)
    has_urgency = any("urgency" in r.get("description", "").lower() or r.get("rule_id") == "urgency_language" for r in triggered_rules)
    has_credentials = any("password" in r.get("description", "").lower() or "credential" in r.get("description", "").lower() or r.get("rule_id") == "credential_request" for r in triggered_rules)
    has_prize = any("prize" in r.get("description", "").lower() or "lottery" in r.get("description", "").lower() or r.get("rule_id") == "prize_scam" for r in triggered_rules)
    has_typosquatting = any(r.get("rule_id") == "typosquatting" for r in triggered_rules)
    has_ip = any(r.get("rule_id") == "ip_based" for r in triggered_rules)
    has_shortener = any(r.get("rule_id") == "url_shortener" for r in triggered_rules)
    has_threat = any(r.get("rule_id") == "threat_language" for r in triggered_rules)

    # Lead summary based on the primary attack vector
    if has_banking and has_urgency and has_credentials:
        explanations.append("[Critical Banking Phishing Attempt] Attackers are using false urgency (e.g. account suspension) to pressure you into submitting your confidential bank credentials or OTPs.")
    elif has_prize:
        explanations.append("[Lottery / Advance-Fee Fraud] Uses fake winnings or rewards to lure you into sharing banking information or paying fraudulent processing fees.")
    elif has_typosquatting:
        explanations.append("[Brand Impersonation / Typosquatting] Deceptive domain designed to mimic a trusted service and trick users into entering credentials on a spoofed login portal.")
    elif has_banking:
        explanations.append("[Financial Harvesting Alert] Unverified message requesting payment cards, account details, or PINs.")
    elif has_urgency and has_threat:
        explanations.append("[Coercive Threat Language] Uses panic-inducing claims (police action, legal penalties, permanent account deletion) to prevent rational verification.")

    # Detailed itemized rules
    for rule in triggered_rules:
        desc = rule.get("description", "")
        if desc:
            explanations.append(f"- {desc}")

    return "\n".join(explanations)


def generate_recommendations(verdict: str, threat_type: str = "general", input_text: str = "") -> tuple:
    recommendation = ""
    tips = []
    text_lower = input_text.lower() if input_text else ""
    
    if verdict == "Safe":
        if any(k in text_lower for k in ["otp", "verification code"]):
            recommendation = "Standard security verification code. Safe to use for your ongoing transaction."
            tips = [
                "Never share your OTP with anyone over a phone call or chat, even if they claim to be bank officials.",
                "Verify that you initiated this transaction before using the code."
            ]
        else:
            recommendation = "This content appears safe and clean of common phishing heuristics."
            tips = [
                "Always verify the sender's identity when handling sensitive operations.",
                "Keep your web browser and operating system security patches up to date."
            ]
            
    elif verdict == "Suspicious":
        recommendation = "Exercise heightened caution. Potential risk indicators were identified."
        if "http" in text_lower or threat_type == "phishing URL":
            tips = [
                "Do not enter passwords, PINs, or card numbers on this website.",
                "If this is from a known company, visit their official app or website directly instead of clicking this link.",
                "Check the browser address bar carefully for spelling anomalies."
            ]
        else:
            tips = [
                "Verify the sender's identity through a trusted alternative channel.",
                "Do not forward or reply to this message until confirmed safe.",
                "Never share personal identification or financial numbers."
            ]
            
    else:  # Dangerous
        if any(k in text_lower for k in ["bank", "sbi", "hdfc", "icici", "axis", "account", "pan", "kyc"]):
            recommendation = "High-Risk Banking Scam Detected! Immediate action required to protect your funds."
            tips = [
                "Do NOT click any link or call the phone number provided in this message.",
                "Banks NEVER ask for passwords, CVVs, or OTPs via SMS or unverified links.",
                "If you entered any data, immediately freeze your card/account via your official banking app and call your bank's 24x7 helpline."
            ]
        elif any(k in text_lower for k in ["winner", "prize", "lottery", "gift", "crore", "lakh", "reward"]):
            recommendation = "Fraudulent Reward / Lottery Scam. Disregard completely."
            tips = [
                "Legitimate organizations do not demand processing fees or bank verification to claim prizes.",
                "Block and report the sender immediately on WhatsApp / SMS.",
                "Never send money or share bank account numbers."
            ]
        elif threat_type == "phishing URL" or "http" in text_lower:
            recommendation = "Malicious URL Detected. Do not visit or enter any credentials."
            tips = [
                "Close the browser tab immediately.",
                "Do not download files, APKs, or allow browser notifications from this domain.",
                "Clear your browser cookies and cache if you visited the site."
            ]
        elif threat_type == "SMS smishing":
            recommendation = "Malicious Smishing Attempt. Do not interact with this SMS."
            tips = [
                "Block the sender's number on your device.",
                "Report the message as spam to your mobile network provider (e.g. forward to 1909).",
                "Do not reply with any text (e.g. STOP or HELP)."
            ]
        else:
            recommendation = "Dangerous Cyber Threat Detected. Avoid all interaction."
            tips = [
                "Delete this communication immediately.",
                "Never disclose passwords, OTPs, or government IDs.",
                "Report this threat to the national cybercrime portal (cybercrime.gov.in)."
            ]
            
    return recommendation, "\n".join([f"- {tip}" for tip in tips])
