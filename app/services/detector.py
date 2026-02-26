import re

SCAM_PATTERNS = [
    r"lottery",
    r"won\s+₹?\d+",
    r"claim\s+now",
    r"urgent",
    r"immediately",
    r"account\s+blocked",
    r"verify\s+otp",
    r"click\s+this\s+link",
    r"work\s+from\s+home",
    r"registration\s+fee",
    r"pay\s+₹?\d+",
    r"guaranteed\s+income",
    r"limited\s+offer",
    r"free\s+gift",
]

def detect_scam(message: str):
    score = 0
    matches = []

    for pattern in SCAM_PATTERNS:
        if re.search(pattern, message, re.IGNORECASE):
            score += 1
            matches.append(pattern)

    label = "SCAM" if score >= 2 else "SAFE"

    return {
        "label": label,
        "score": score,
        "matched_rules": matches
    }