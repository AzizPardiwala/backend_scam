import re
import pickle
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

model = pickle.load(open(os.path.join(BASE_DIR, "ai/model.pkl"), "rb"))
vectorizer = pickle.load(open(os.path.join(BASE_DIR, "ai/vectorizer.pkl"), "rb"))

def detect_scam(message: str):
    text = message.lower()

    # 🔗 phishing detection
    if "http" in text or "www" in text:
        if "bit.ly" in text or "tinyurl" in text:
            return {
                "label": "SCAM",
                "confidence": 0.97,
                "reason": "Suspicious shortened URL",
                "type": "phishing"
            }

    # 🔥 keywords
    if any(word in text for word in ["win", "prize", "lottery"]):
        return {
            "label": "SCAM",
            "confidence": 0.95,
            "reason": "Lottery keywords detected",
            "type": "lottery"
        }

    vec = vectorizer.transform([message])
    pred = model.predict(vec)[0]
    prob = model.predict_proba(vec).max()

    return {
        "label": pred,
        "confidence": float(prob),
        "reason": "ML prediction",
        "type": "unknown"
    }