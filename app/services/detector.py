# This is rule-based detection (Stage 1)
# Later we replace with ML model.

SCAM_KEYWORDS = [
    "lottery",
    "winner",
    "free money",
    "click this link",
    "urgent",
    "account suspended",
    "send otp",
    "verify now",
]


def detect_scam(message: str):
    message_lower = message.lower()

    matched = [word for word in SCAM_KEYWORDS if word in message_lower]

    if matched:
        return {
            "is_scam": True,
            "confidence": min(0.5 + len(matched) * 0.1, 0.95),
            "reason": f"Detected suspicious keywords: {', '.join(matched)}",
        }

    return {
        "is_scam": False,
        "confidence": 0.2,
        "reason": "No scam indicators detected",
    }
