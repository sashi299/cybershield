import re
from urllib.parse import urlparse

def analyze_url_rules(url: str) -> dict:
    score = 0
    triggered_rules = []
    
    def add_rule(rule_id, description, severity, weight):
        nonlocal score
        triggered_rules.append({"rule_id": rule_id, "description": description, "severity": severity})
        score += weight

    try:
        parsed_url = urlparse(url)
    except Exception:
        add_rule("invalid_url", "URL is malformed.", "high", 100)
        return {"score": min(100, score), "triggered_rules": triggered_rules}

    domain = parsed_url.netloc.lower()
    path = parsed_url.path.lower()
    scheme = parsed_url.scheme.lower()
    full_url_lower = url.lower()

    if re.match(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}(:[0-9]+)?$", domain):
        add_rule("ip_based", "URL uses an IP address instead of a domain name.", "high", 60)

    domain_parts = domain.split('.')
    if len(domain_parts) > 4:
        add_rule("excessive_subdomains", "URL has an unusually high number of subdomains.", "medium", 40)

    shorteners = {'bit.ly', 'tinyurl.com', 't.co', 'is.gd', 'goo.gl', 'ow.ly', 'rebrand.ly', 'cutt.ly', 'shorturl.at'}
    if any(domain == s or domain.endswith('.' + s) for s in shorteners):
        add_rule("url_shortener", "URL uses a shortening service often abused by phishers.", "medium", 35)

    popular_domains = ['google', 'paypal', 'amazon', 'microsoft', 'apple', 'facebook', 'netflix', 'instagram', 'twitter', 'linkedin', 'bank', 'chase', 'wells', 'citibank', 'flipkart', 'ebay', 'walmart']
    for pd in popular_domains:
        if pd in domain and pd not in domain.split('.'):
            add_rule("typosquatting", f"Domain contains '{pd}' but appears to be a deceptive imitation.", "high", 70)
            break

    if scheme != 'https' and scheme != '':
        add_rule("missing_https", "Connection is not secure (missing HTTPS).", "low", 20)

    suspicious_keywords = ['verify', 'suspended', 'unauthorized', 'immediately', 'urgent', 'confirm', 'limited time', 'act now', 'click here', 'update your', 'expire', 'alert', 'warning', 'congratulations', 'winner', 'prize', 'free', 'offer', 'risk', 'compromised', 'locked', 'disabled', 'unusual activity']
    for kw in suspicious_keywords:
        if kw.replace(' ', '') in full_url_lower or kw.replace(' ', '-') in full_url_lower:
            add_rule("suspicious_keyword", f"URL contains suspicious keyword: '{kw}'.", "high", 30)
            break

    suspicious_tlds = ['.xyz', '.tk', '.ml', '.ga', '.cf', '.top', '.buzz', '.club', '.info', '.work', '.click', '.link', '.gq', '.pw']
    if any(domain.endswith(tld) for tld in suspicious_tlds):
        add_rule("suspicious_tld", "Domain uses a top-level domain frequently associated with spam or malicious activity.", "medium", 45)

    if '@' in url:
        add_rule("at_sign", "URL contains an '@' symbol, often used to hide the true destination.", "high", 65)

    if len(url) > 75:
        add_rule("excessive_length", "URL is abnormally long, which may hide its true intent.", "low", 15)

    if scheme == 'data':
        add_rule("data_uri", "URL uses a data URI scheme which is suspicious for external links.", "high", 80)

    # DGA / Randomly generated domain name check
    domain_parts_clean = domain.split(':')[0].split('.')
    if len(domain_parts_clean) >= 2:
        main_name = domain_parts_clean[-2]
        if len(main_name) >= 4 and not main_name.isdigit():
            vowels = set('aeiou')
            vowel_count = sum(1 for c in main_name if c in vowels)
            vowel_ratio = vowel_count / len(main_name)
            has_consonant_cluster = bool(re.search(r'[bcdfghjklmnpqrstvwxyz]{4,}', main_name))
            if (vowel_ratio < 0.15 and len(main_name) >= 4) or (has_consonant_cluster and len(main_name) >= 5):
                add_rule("random_domain_structure", f"Domain name '{main_name}' appears randomly generated or unbranded (DGA pattern).", "medium", 35)

    return {
        "score": min(100, score),
        "triggered_rules": triggered_rules
    }

def analyze_text_rules(text: str) -> dict:
    """Analyze raw text content (email/SMS) for phishing indicators."""
    score = 0
    triggered_rules = []
    
    def add_rule(rule_id, description, severity, weight):
        nonlocal score
        triggered_rules.append({"rule_id": rule_id, "description": description, "severity": severity})
        score += weight

    text_lower = text.lower()
    
    safe_context_patterns = [
        r'your otp (?:is|for)\s*[:\s]*\d{4,8}',
        r'do not share (?:this|your|the) (?:otp|code|pin)',
        r'(?:order|package|shipment)\s*#?\s*[a-z0-9-]{5,}',
        r'(?:has shipped|has been delivered|out for delivery)'
    ]
    is_likely_legitimate = False
    for pattern in safe_context_patterns:
        if re.search(pattern, text_lower):
            is_likely_legitimate = True
            break
    
    # Urgency/action keywords
    urgency_keywords = [
        'verify your account', 'account suspended', 'unauthorized access',
        'immediate action required', 'act now', 'click here', 'update your payment',
        'confirm your identity', 'limited time offer', 'your account will be closed',
        'unusual activity', 'security alert', 'verify now', 'expire', 'suspended',
        'compromised', 'locked', 'disabled'
    ]
    found_urgency = [kw for kw in urgency_keywords if kw in text_lower]
    if found_urgency and not is_likely_legitimate:
        add_rule("urgency_language", f"Contains urgency/pressure language: '{found_urgency[0]}'.", "high", min(30 + len(found_urgency) * 5, 50))
    
    # Prize/lottery scam indicators
    prize_keywords = ['congratulations', 'winner', 'won a prize', 'lottery', 'lucky', 'selected', 'claim your']
    found_prizes = [kw for kw in prize_keywords if kw in text_lower]
    if found_prizes:
        add_rule("prize_scam", f"Contains prize/lottery scam language: '{found_prizes[0]}'.", "high", 40)
    
    # Financial information requests
    financial_keywords = ['credit card', 'bank account', 'social security', 'ssn', 'routing number', 'pin number', 'cvv', 'billing address', 'wire transfer']
    found_financial = [kw for kw in financial_keywords if kw in text_lower]
    if found_financial:
        add_rule("financial_request", f"Requests sensitive financial information: '{found_financial[0]}'.", "high", 45)
    
    # Credential requests
    credential_keywords = ['password', 'username', 'login credentials', 'otp', 'one-time', 'verification code']
    found_creds = [kw for kw in credential_keywords if kw in text_lower]
    if found_creds:
        safe_creds = {'otp', 'verification code'}
        only_safe_creds = all(kw in safe_creds for kw in found_creds)
        if not (is_likely_legitimate and only_safe_creds):
            add_rule("credential_request", f"Requests login credentials or verification codes: '{found_creds[0]}'.", "high", 40)

    # Impersonation indicators
    impersonation = ['dear customer', 'dear user', 'dear valued', 'dear account holder', 'dear sir/madam']
    found_impersonation = [kw for kw in impersonation if kw in text_lower]
    if found_impersonation:
        add_rule("impersonation", "Uses generic greeting typical of phishing messages.", "medium", 20)
    
    # Threat of consequences
    threat_keywords = ['will be terminated', 'will be suspended', 'will be closed', 'legal action', 'law enforcement', 'failure to respond']
    found_threats = [kw for kw in threat_keywords if kw in text_lower]
    if found_threats:
        add_rule("threat_language", f"Contains threatening language: '{found_threats[0]}'.", "high", 35)

    has_suspicious_url = False
    urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
    for url in urls:
        url_result = analyze_url_rules(url)
        if url_result['score'] > 0:
            has_suspicious_url = True
            break
            
    if found_urgency and found_creds and has_suspicious_url:
        add_rule("combined_phishing_signals", "Contains urgency language, requests credentials, and has a suspicious URL.", "high", 50)

    return {
        "score": min(100, score),
        "triggered_rules": triggered_rules
    }
