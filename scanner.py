import re
from urllib.parse import urlparse

MESSAGE_RULES = [
    ("Upfront payment request", r"\b(registration|processing|security|training|interview|joining)\s+(fee|fees|charge|payment)\b|\bpay\s+(now|today|immediately)\b", 28,
     "Legitimate employers generally do not ask candidates to pay to secure a job or interview."),
    ("Sensitive information request", r"\b(otp|one[- ]time password|password|pin|cvv|card number|bank details)\b", 35,
     "Never share OTPs, passwords, PINs or card security details with an unknown sender."),
    ("Urgency or pressure tactic", r"\b(urgent|immediately|today only|limited time|last chance|within \d+ hours|act now)\b", 15,
     "Scammers often pressure people to act before they can verify an offer."),
    ("Unusually attractive reward", r"\b(guaranteed|earn|salary|work from home|per day|per month|selected)\b", 8,
     "Unusually attractive or guaranteed offers should be independently verified."),
    ("Suspicious link included", r"(https?://|www\.)", 12,
     "Avoid opening unexpected links. Check the domain independently before entering information."),
    ("Personal email used for recruitment", r"\b(gmail\.com|yahoo\.com|outlook\.com)\b", 8,
     "A personal email address is not proof of fraud, but verify the recruiter through the company's official website."),
    ("Request to move conversation", r"\b(telegram|whatsapp|signal)\b", 5,
     "Moving a recruitment conversation to a messaging app can reduce traceability. Verify the sender.")
]

def _level(score):
    if score >= 60:
        return "High"
    if score >= 30:
        return "Medium"
    return "Low"

def scan_message(text):
    findings = []
    score = 0
    for title, pattern, weight, advice in MESSAGE_RULES:
        if re.search(pattern, text, re.IGNORECASE):
            score += weight
            findings.append({"title": title, "advice": advice, "weight": weight})

    score = min(score, 100)
    if not findings:
        findings.append({
            "title": "No configured warning pattern found",
            "advice": "This does not prove the message is safe. Verify the sender and offer through an official channel.",
            "weight": 0
        })

    level = _level(score)
    return {
        "type": "message",
        "score": score,
        "level": level,
        "summary": {
            "High": "Several warning signs were detected. Do not pay or share sensitive information.",
            "Medium": "Some warning signs were detected. Verify independently before responding.",
            "Low": "Few configured warning signs were detected. Still verify the sender before trusting it."
        }[level],
        "findings": findings,
        "recommendations": [
            "Do not pay a fee to secure a job, prize or internship.",
            "Never share OTPs, passwords, PINs or banking credentials.",
            "Contact the organisation using contact details from its official website.",
            "If money has already been lost in India, contact the cybercrime helpline 1930 promptly and report at cybercrime.gov.in."
        ],
        "disclaimer": "Prototype result based on keyword rules. It is not a verified fraud determination or a calibrated probability."
    }

def scan_url(raw):
    candidate = raw.strip()
    if not re.match(r"^https?://", candidate, re.IGNORECASE):
        candidate = "https://" + candidate
    parsed = urlparse(candidate)
    host = (parsed.hostname or "").lower()
    findings = []
    score = 0

    def add(title, advice, weight):
        nonlocal score
        score += weight
        findings.append({"title": title, "advice": advice, "weight": weight})

    if not host or "." not in host:
        add("URL format looks incomplete", "Check the address carefully and use the organisation's official website.", 25)
    if parsed.scheme != "https":
        add("No HTTPS connection indicated", "Do not enter passwords or payment details on a site without HTTPS.", 12)
    if re.search(r"(^|\.)xn--", host):
        add("Internationalised domain encoding", "Check for look-alike characters and confirm the exact domain.", 20)
    if re.search(r"\d{4,}", host):
        add("Many digits in the domain", "Unexpected numbers in a domain can be suspicious. Verify the official address.", 10)
    if len(host) > 35:
        add("Unusually long domain", "Long or confusing domains can imitate trusted brands. Verify the spelling.", 10)
    if host.count("-") >= 2:
        add("Multiple hyphens in domain", "Check whether the domain is impersonating a known organisation.", 8)
    if re.search(r"(login|verify|secure|update|wallet|bonus|claim|free|gift)", candidate, re.IGNORECASE):
        add("Sensitive or reward-related wording", "A URL containing these words is not automatically malicious. Verify it before opening.", 10)
    if re.search(r"(bit\.ly|tinyurl\.com|t\.co|shorturl\.at)", host):
        add("URL shortener detected", "Short links hide the final destination. Confirm the destination with the sender first.", 18)
    if "@" in parsed.netloc:
        add("Unexpected @ symbol in address", "The part before @ can mislead users about the actual destination.", 25)

    score = min(score, 100)
    if not findings:
        findings.append({
            "title": "No configured URL warning pattern found",
            "advice": "This check does not establish that the website is safe. Confirm the domain independently.",
            "weight": 0
        })

    level = _level(score)
    return {
        "type": "url",
        "score": score,
        "level": level,
        "summary": {
            "High": "Multiple URL warning signs were detected. Avoid opening it until independently verified.",
            "Medium": "Some URL warning signs were detected. Verify the domain before continuing.",
            "Low": "Few configured URL warning signs were detected. This is not a safety guarantee."
        }[level],
        "findings": findings,
        "recommendations": [
            "Do not open unexpected links from unknown senders.",
            "Check the spelling of the domain letter by letter.",
            "Visit the organisation by typing its known official address yourself.",
            "Never enter OTPs, passwords or payment details after following an unsolicited link."
        ],
        "disclaimer": "The prototype checks URL structure only. It does not visit the URL, check live threat feeds, or confirm whether a site is malicious."
    }
