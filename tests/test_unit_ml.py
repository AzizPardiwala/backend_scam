"""
UNIT TESTS — ML Service (no DB, no HTTP)
Tests: scam prediction model
"""
import pytest
from app.services.ml_service import predict, model, vectorizer


class TestMLPredict:

    def test_returns_tuple(self):
        result = predict("You won a lottery, send your bank details now")
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_prediction_is_string(self):
        label, conf = predict("Click here to claim your prize money")
        assert isinstance(label, str)

    def test_confidence_is_float_between_0_and_1(self):
        label, conf = predict("Urgent: your account will be blocked")
        assert isinstance(conf, float)
        assert 0.0 <= conf <= 1.0

    def test_obvious_scam_detected(self):
        label, conf = predict(
            "Congratulations! You have won Rs 50 lakh lottery. "
            "Send your Aadhaar and bank account number to claim."
        )
        assert label == "SCAM"
        assert conf > 0.5

    def test_normal_message_not_scam(self):
        label, conf = predict("Hi, can we meet tomorrow for lunch?")
        assert label == "NOT_SCAM"

    def test_empty_string_returns_result(self):
        label, conf = predict("")
        assert label in ("SCAM", "NOT_SCAM", "UNKNOWN")

    def test_long_text_works(self):
        long_text = "This is a scam message. " * 100
        label, conf = predict(long_text)
        assert label in ("SCAM", "NOT_SCAM")

    def test_model_loaded(self):
        assert model is not None, "ML model failed to load"

    def test_vectorizer_loaded(self):
        assert vectorizer is not None, "Vectorizer failed to load"