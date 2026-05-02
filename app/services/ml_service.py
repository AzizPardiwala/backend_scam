import pickle
import os

# Get project base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ✅ Correct path (ai folder, not ml)
model_path = os.path.join(BASE_DIR, "ai", "model.pkl")
vectorizer_path = os.path.join(BASE_DIR, "ai", "vectorizer.pkl")

# Load files
model = pickle.load(open(model_path, "rb"))
vectorizer = pickle.load(open(vectorizer_path, "rb"))


def predict(text: str):
    vec = vectorizer.transform([text])
    pred = model.predict(vec)[0]
    prob = max(model.predict_proba(vec)[0])

    return pred, float(prob)