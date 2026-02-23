import re

class ScamDetector:

    def __init__(self):
        self.scam_patterns = [
            r"win.*money",
            r"free.*gift",
            r"urgent.*action",
            r"click.*link",
            r"share.*otp",
            r"bank.*suspended",
            r"lottery.*won",
            r"claim.*prize",
            r"verify.*account",
        ]

    def analyze(self, text: str):
        text = text.lower()

        matches = 0

        for pattern in self.scam_patterns:
            if re.search(pattern, text):
                matches += 1

        confidence = min(matches / len(self.scam_patterns) * 100, 95)

        is_scam = matches > 0

        explanation = (
            f"Detected {matches} suspicious pattern(s)"
            if is_scam else
            "Message looks safe"
        )

        return {
            "is_scam": is_scam,
            "confidence": round(confidence, 2),
            "explanation": explanation
        }
