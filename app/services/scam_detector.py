import re
from datetime import datetime, timezone

SCAM_PATTERNS = [
    r"lottery",
    r"win money",
    r"claim now",
    r"urgent",
    r"account blocked",
    r"verify your account",
    r"click this link",
]

def detect_scam(message: str):
    message_lower = message.lower()
    score = 0
    matched_rules = []

    for pattern in SCAM_PATTERNS:
        if re.search(pattern, message_lower):
            score += 1
            matched_rules.append(pattern)

    label = "SCAM" if score >= 2 else "SAFE"

    return {
        "label": label,
        "score": score,
        "matched_rules": matched_rules,
        "analyzed_at": datetime.now(timezone.utc).isoformat()
    }