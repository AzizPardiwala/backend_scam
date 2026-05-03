import pickle
import os
from app.core.logger import logger

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_path = os.path.join(BASE_DIR, "ai", "model.pkl")
vectorizer_path = os.path.join(BASE_DIR, "ai", "vectorizer.pkl")

try:
    model = pickle.load(open(model_path, "rb"))
    vectorizer = pickle.load(open(vectorizer_path, "rb"))
    logger.info("ML model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load ML model: {e}")
    model = None
    vectorizer = None


def predict(text: str) -> tuple[str, float]:
    """
    SYNCHRONOUS ML prediction.
    Returns (prediction_label, confidence_score).
    """
    if not model or not vectorizer:
        return "UNKNOWN", 0.0

    vec = vectorizer.transform([text])
    pred = model.predict(vec)[0]
    prob = float(max(model.predict_proba(vec)[0]))
    return str(pred), prob