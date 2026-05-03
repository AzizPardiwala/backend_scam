import os
import json
from app.core.logger import logger

try:
    import google.generativeai as genai
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        GEMINI_MODEL = genai.GenerativeModel("gemini-pro")
        GEMINI_AVAILABLE = True
    else:
        GEMINI_AVAILABLE = False
        logger.warning("GEMINI_API_KEY not set — Gemini classification disabled")
except Exception as e:
    GEMINI_AVAILABLE = False
    logger.warning(f"Gemini not available: {e}")

SYSTEM_PROMPT = """
You are a cybersecurity expert specializing in Indian online scams.

Classify the scam report into ONE of these types:
JOB_SCAM, BANK_CALL, UPI_FRAUD, INVESTMENT_SCAM, CRYPTO_SCAM,
LOAN_SCAM, LOTTERY_SCAM, ROMANCE_SCAM, ONLINE_SHOPPING_SCAM, OTHER

Return ONLY valid JSON — no markdown, no extra text:
{
  "scam_type": "TYPE",
  "risk_score": 1-10,
  "reason": "one sentence explanation"
}
"""


def classify_scam(description: str) -> dict:
    """
    SYNCHRONOUS Gemini classification.
    Returns dict with scam_type, risk_score, reason.
    """
    if not GEMINI_AVAILABLE:
        return {
            "scam_type": "OTHER",
            "risk_score": 5,
            "reason": "AI classification unavailable — no API key configured"
        }

    try:
        prompt = SYSTEM_PROMPT + f"\n\nScam report:\n{description}"
        response = GEMINI_MODEL.generate_content(prompt)
        text = response.text.strip()

        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]

        return json.loads(text.strip())

    except json.JSONDecodeError:
        logger.warning("Gemini returned non-JSON response")
        return {"scam_type": "OTHER", "risk_score": 5, "reason": "AI could not parse the report clearly"}
    except Exception as e:
        logger.error(f"Gemini error: {e}")
        return {"scam_type": "OTHER", "risk_score": 3, "reason": "AI classification failed"}