import pickle
import re
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

model_path = os.path.join(BASE_DIR, "ai", "model.pkl")
vectorizer_path = os.path.join(BASE_DIR, "ai", "vectorizer.pkl")

model = pickle.load(open(model_path, "rb"))
vectorizer = pickle.load(open(vectorizer_path, "rb"))

def detect_scam(message: str):

    text = message.lower()

    scam_keywords = {
        "lottery": ["win", "won", "prize", "lottery", "reward"],
        "phishing": ["verify", "kyc", "account blocked", "bank", "upi"],
        "otp fraud": ["otp", "urgent", "do not share"],
        "clickbait": ["click here", "free", "gift", "cashback"]
    }

    for scam_type, keywords in scam_keywords.items():
        for word in keywords:
            if re.search(rf"\b{re.escape(word)}\b", text):
                return {
                    "label": "SCAM",
                    "confidence": 0.95,
                    "reason": f"Detected keyword '{word}' related to {scam_type}",
                    "type": scam_type
                }

    vectorized = vectorizer.transform([message])
    prediction = model.predict(vectorized)[0]
    prob = model.predict_proba(vectorized).max()

    return {
        "label": prediction,
        "confidence": float(prob),
        "reason": "Predicted using ML model",
        "type": "unknown"
    }