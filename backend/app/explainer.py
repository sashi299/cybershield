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
            elif any(k in text_lower for k in ["order", "shipped", "delivered", "tracking", "package", "out for delivery"]):
                return "Genuine shipping / service update. No phishing links, urgency coercion, or suspicious requests for sensitive personal details detected."
            elif any(k in text_lower for k in ["meeting", "interview", "schedule", "zoom", "calendar", "call"]):
                return "Standard business communication. Verified sender intent with no coercive phishing vectors or credential harvesting patterns."
            else:
                return "Normal conversational text. Analysis found no psychological manipulation, fake urgency, lottery claims, financial requests, or malicious redirect links."
        return "No suspicious patterns or threat indicators were detected."

    # 2. Dynamic, context-specific threat breakdown for triggered rules
    explanations = []
    
    # Specific attack pattern detections
    is_electricity = any(k in text_lower for k in ["electricity", "power", "bill", "disconnected", "officer"])
    is_job_scam = any(k in text_lower for k in ["part time", "earn daily", "telegram", "like video", "subscribe", "work from home", "salary"])
    is_tax_scam = any(k in text_lower for k in ["income tax", "refund", "it dept", "it department", "tax refund"])
    is_sim_scam = any(k in text_lower for k in ["sim", "esim", "5g upgrade", "kyc expired", "sim block"])
    is_delivery_scam = any(k in text_lower for k in ["customs", "delivery fee", "address update", "package hold", "parcel stuck"])
    
    # Heuristic category flags
    has_banking = any("bank" in r.get("description", "").lower() or "financial" in r.get("description", "").lower() or r.get("rule_id") == "financial_request" for r in triggered_rules)
    has_urgency = any("urgency" in r.get("description", "").lower() or r.get("rule_id") == "urgency_language" for r in triggered_rules)
    has_credentials = any("password" in r.get("description", "").lower() or "credential" in r.get("description", "").lower() or r.get("rule_id") == "credential_request" for r in triggered_rules)
    has_prize = any("prize" in r.get("description", "").lower() or "lottery" in r.get("description", "").lower() or r.get("rule_id") == "prize_scam" for r in triggered_rules)
    has_typosquatting = any(r.get("rule_id") == "typosquatting" for r in triggered_rules)
    has_ip = any(r.get("rule_id") == "ip_based" for r in triggered_rules)
    has_shortener = any(r.get("rule_id") == "url_shortener" for r in triggered_rules)
    has_threat = any(r.get("rule_id") == "threat_language" for r in triggered_rules)

    # Lead summary based on the primary attack vector
    if is_electricity:
        explanations.append("[Utility / Electricity Disconnection Scam] Fraudsters use false threats of imminent power disconnection to coerce victims into calling fake officer numbers or downloading remote access APKs.")
    elif is_job_scam:
        explanations.append("[Task / Part-Time Job Scam] Lures victims with promises of easy daily earnings (e.g. liking videos, rating apps) leading into fraudulent crypto or prepaid recharge tasks.")
    elif is_tax_scam:
        explanations.append("[Income Tax Refund Phishing] Impersonates the Tax Department to harvest PAN cards, banking logins, and refund credit card data.")
    elif is_sim_scam:
        explanations.append("[SIM / KYC Block Scam] False warning that your SIM card or KYC is expiring, aiming to trick you into performing unauthorized SIM swaps or sharing Aadhaar/PAN details.")
    elif is_delivery_scam:
        explanations.append("[Parcel / Delivery Redirection Fraud] Fake failed-delivery notice demanding a small fee or address verification to steal card credentials.")
    elif has_banking and (has_urgency or has_credentials):
        explanations.append("[Critical Banking Phishing Attempt] Attackers are using false urgency (e.g. account suspension, KYC update) to pressure you into submitting confidential bank credentials or OTPs.")
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
        if any(k in text_lower for k in ["otp", "verification code", "one time password"]):
            recommendation = "Standard security verification code. Safe to use for your ongoing transaction."
            tips = [
                "Never share your OTP with anyone over a phone call, chat, or email.",
                "Ensure that you personally initiated this transaction before entering the code.",
                "Banks and legitimate services will NEVER call to ask for your OTP."
            ]
        elif any(k in text_lower for k in ["order", "shipped", "delivered", "package"]):
            recommendation = "Verified legitimate delivery / service notification."
            tips = [
                "Track packages directly through the merchant's official mobile application.",
                "Never pay unexpected cash-on-delivery charges for unverified packages."
            ]
        else:
            recommendation = "This content appears clean and safe from common phishing heuristics."
            tips = [
                "Continue using standard online security precautions.",
                "Always check for HTTPS and correct domain spelling when entering passwords."
            ]
            
    elif verdict == "Suspicious":
        recommendation = "Exercise heightened caution. Potential risk indicators were identified."
        if "http" in text_lower or threat_type == "phishing URL":
            tips = [
                "Do NOT enter passwords, PINs, or card details on this website.",
                "If this claims to be from a known company, open their official app or website directly instead of clicking this link.",
                "Inspect the browser address bar for subtle spelling tricks or strange domain extensions."
            ]
        else:
            tips = [
                "Verify the sender's identity through an independent, trusted channel before responding.",
                "Do not forward or click any links inside this communication.",
                "Never disclose personal identification or financial numbers."
            ]
            
    else:  # Dangerous
        if any(k in text_lower for k in ["electricity", "power", "bill", "disconnected"]):
            recommendation = "Electricity Bill Fraud Detected! Do not contact the provided phone number."
            tips = [
                "Electricity boards NEVER send personal mobile numbers for bill payments or disconnections.",
                "Pay electricity bills only through official government portals or verified payment apps.",
                "Do not download any APK files (e.g. QuickSupport, AnyDesk) requested by the sender."
            ]
        elif any(k in text_lower for k in ["part time", "earn daily", "telegram", "like video", "subscribe", "salary"]):
            recommendation = "Fake Job / Task Scam Detected! Disregard and block the sender."
            tips = [
                "Legitimate employers do not recruit through random WhatsApp / Telegram messages with daily payout promises.",
                "Never pay any 'registration fee' or 'security deposit' to unlock work tasks.",
                "Block and report the sender's number on WhatsApp / Telegram immediately."
            ]
        elif any(k in text_lower for k in ["bank", "sbi", "hdfc", "icici", "axis", "account", "pan", "kyc", "debit", "credit"]):
            recommendation = "High-Risk Banking Scam Detected! Immediate protective action required."
            tips = [
                "Do NOT click any link or call the phone number provided in this message.",
                "Banks NEVER ask you to update KYC, PAN, or passwords via SMS links or WhatsApp.",
                "If you entered any details, immediately freeze your card/account via your official banking app and call your bank's 24x7 helpline."
            ]
        elif any(k in text_lower for k in ["winner", "prize", "lottery", "gift", "crore", "lakh", "reward", "congratulations"]):
            recommendation = "Fraudulent Reward / Lottery Scam. Disregard completely."
            tips = [
                "You cannot win a lottery or contest you never entered.",
                "Never pay any 'processing fee', 'GST charge', or 'customs clearance' to claim prizes.",
                "Block and report the sender immediately."
            ]
        elif threat_type == "phishing URL" or "http" in text_lower:
            recommendation = "Malicious URL Detected. Do not visit or enter any credentials."
            tips = [
                "Close the browser tab immediately.",
                "Do not download files, APKs, or allow browser notifications from this domain.",
                "Clear your browser cache and cookies if you already loaded the page."
            ]
        elif threat_type == "SMS smishing":
            recommendation = "Malicious Smishing Attempt. Do not interact with this SMS."
            tips = [
                "Block the sender's number on your mobile device.",
                "Report the message as spam to your mobile network provider (SMS to 1909 in India).",
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
