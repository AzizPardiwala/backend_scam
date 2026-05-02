import os
import pickle

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

model_path = os.path.join(BASE_DIR, "ai/model.pkl")
vectorizer_path = os.path.join(BASE_DIR, "ai/vectorizer.pkl")

model = pickle.load(open(model_path, "rb"))
vectorizer = pickle.load(open(vectorizer_path, "rb"))


def detect_scam(message: str):
    vectorized = vectorizer.transform([message])

    prediction = model.predict(vectorized)[0]

    # Confidence (if available)
    try:
        confidence = max(model.predict_proba(vectorized)[0])
    except:
        confidence = 0.9

    return {
        "prediction": str(prediction),
        "confidence": float(confidence)
    }