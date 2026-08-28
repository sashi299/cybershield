def explain_rules(triggered_rules: list, input_type: str = "url") -> str:
    if not triggered_rules:
        if input_type == "url":
            return "Legitimate domain structure. Standard protocol and registered domain verified with no typosquatting, blacklisted TLDs, IP hostnames, or deceptive patterns detected."
        elif input_type in ("email", "sms", "text"):
            return "Standard conversational message. No urgency pressure tactics, lottery/prize scam keywords, credential harvesting requests, or suspicious links detected."
        return "No suspicious patterns or threat indicators were detected."
    
    explanations = []
    for rule in triggered_rules:
        explanations.append(f"- {rule['description']}")
    return "\n".join(explanations)

def generate_recommendations(verdict: str, threat_type: str = "general") -> tuple:
    recommendation = ""
    tips = []
    
    if verdict == "Safe":
        recommendation = "This looks safe, but always remain cautious online."
        tips = [
            "Always verify the sender's identity before clicking links.",
            "Keep your browser and security software updated."
        ]
    elif verdict == "Suspicious":
        recommendation = "Exercise caution. There are signs this might be unsafe."
        tips = [
            "Do not enter any personal or financial information.",
            "If this is from a known entity, navigate to their official site manually instead of using this link."
        ]
    else:
        recommendation = "Do not proceed. This is highly likely to be a threat."
        
        if threat_type == "phishing URL":
            tips = [
                "Close the tab immediately.",
                "Do not download any files or run any scripts from this site.",
                "If you entered information, change your passwords and contact your bank if necessary."
            ]
        elif threat_type == "email scam":
            tips = [
                "Mark the email as spam and delete it.",
                "Do not reply to the sender or open any attachments.",
                "Never share OTPs, passwords, or personal details."
            ]
        elif threat_type == "SMS smishing":
            tips = [
                "Block the sender's number on your phone.",
                "Do not tap on the link.",
                "Report the message as spam to your carrier."
            ]
        else:
            tips = [
                "Avoid interacting with this content entirely.",
                "Report this to the relevant platform or authority."
            ]
            
    return recommendation, "\n".join([f"- {tip}" for tip in tips])
