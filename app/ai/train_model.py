import pandas as pd
import pickle

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LogisticRegression
from sklearn.utils import resample


# ===============================
# 1. Load dataset (TSV FIX)
# ===============================

data = pd.read_csv(
    "app/ai/scam_dataset.csv",
    sep="\t",
    names=["label", "text"]
)

# Remove empty rows
data = data.dropna()


# ===============================
# 2. Convert labels
# ===============================

data["label"] = data["label"].map({
    "ham": "NOT_SCAM",
    "spam": "SCAM"
})

# Remove invalid rows
data = data.dropna()


# ===============================
# 3. Add Indian scam patterns
# ===============================

extra_data = [
    ("SCAM","Congratulations! You won ₹10000 click here"),
    ("SCAM","Your bank account blocked verify KYC immediately"),
    ("SCAM","Your UPI account suspended update now"),
    ("SCAM","Click this link to claim prize money"),
    ("SCAM","Free gift card available click here"),
    ("SCAM","You won lottery claim reward now"),
    ("SCAM","Urgent verify your account or it will be blocked"),
    ("SCAM","Your ATM card blocked update KYC"),
    ("SCAM","You have received cashback click link"),
    ("SCAM","OTP fraud do not share your OTP"),
]

extra_df = pd.DataFrame(extra_data, columns=["label", "text"])

data = pd.concat([data, extra_df], ignore_index=True)


# ===============================
# 4. Balance dataset (IMPORTANT)
# ===============================

df_scam = data[data["label"] == "SCAM"]
df_not_scam = data[data["label"] == "NOT_SCAM"]

df_scam_upsampled = resample(
    df_scam,
    replace=True,
    n_samples=len(df_not_scam),
    random_state=42
)

data = pd.concat([df_not_scam, df_scam_upsampled])


# ===============================
# 5. Prepare data
# ===============================

X = data["text"]
y = data["label"]


# ===============================
# 6. Vectorization (IMPROVED)
# ===============================

vectorizer = TfidfVectorizer(
    stop_words="english",
    ngram_range=(1, 3),   # detects phrases
    max_features=10000
)

X_vectorized = vectorizer.fit_transform(X)


# ===============================
# 7. Train/Test split
# ===============================

X_train, X_test, y_train, y_test = train_test_split(
    X_vectorized,
    y,
    test_size=0.2,
    random_state=42
)


# ===============================
# 8. Train Model (BETTER)
# ===============================

model = LogisticRegression(max_iter=1000)

model.fit(X_train, y_train)


# ===============================
# 9. Evaluate Model
# ===============================

y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)

print("Model Accuracy:", accuracy)


# ===============================
# 10. Save Model
# ===============================

with open("app/ai/model.pkl", "wb") as f:
    pickle.dump(model, f)

with open("app/ai/vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)

print("AI model trained and saved successfully")