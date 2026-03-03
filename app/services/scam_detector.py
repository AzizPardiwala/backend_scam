import re

SCAM_PATTERNS = [
    r"lottery",
    r"win money",
    r"urgent",
    r"account blocked",
    r"verify now",
    r"click here",
    r"bank otp",
    r"free gift"
]

def detect_scam(message: str):
    message_lower = message.lower()
    score = 0
    matched = []

    for pattern in SCAM_PATTERNS:
        if re.search(pattern, message_lower):
            score += 1
            matched.append(pattern)

    confidence = min(score / len(SCAM_PATTERNS), 1.0) * 100
    label = "SCAM" if score >= 2 else "SAFE"

    return {
        "label": label,
        "confidence": round(confidence, 2),
        "matched": matched
    }