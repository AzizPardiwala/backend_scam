import pickle
import os

# Load model + vectorizer
model_path = os.path.join("app", "ai", "model.pkl")
vectorizer_path = os.path.join("app", "ai", "vectorizer.pkl")

with open(model_path, "rb") as f:
    model = pickle.load(f)

with open(vectorizer_path, "rb") as f:
    vectorizer = pickle.load(f)


def detect_scam(message: str):

    text = message.lower()

    # ===============================
    # 1. RULE-BASED DETECTION (STRONG)
    # ===============================

    scam_keywords = [
        "win", "won", "prize", "lottery", "click here",
        "free", "urgent", "verify", "kyc", "otp",
        "account blocked", "bank", "upi", "cashback",
        "₹", "reward", "gift", "claim"
    ]

    if any(word in text for word in scam_keywords):
        return {
            "label": "SCAM",
            "confidence": 0.95
        }

    # ===============================
    # 2. ML MODEL
    # ===============================

    vectorized = vectorizer.transform([message])
    prediction = model.predict(vectorized)[0]
    prob = model.predict_proba(vectorized).max()

    return {
        "label": prediction,
        "confidence": float(prob)
    }