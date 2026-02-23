import google.generativeai as genai
import os
import json

# Use environment variable (PROFESSIONAL PRACTICE)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODEL = genai.GenerativeModel("gemini-pro")

SYSTEM_PROMPT = """
You are a cybersecurity expert.

Classify scam reports into one of these types ONLY:
JOB_SCAM
BANK_CALL
UPI_FRAUD
INVESTMENT_SCAM
CRYPTO_SCAM
LOAN_SCAM
LOTTERY_SCAM
ROMANCE_SCAM
ONLINE_SHOPPING_SCAM
OTHER

Return JSON only in this format:
{
  "scam_type": "TYPE",
  "risk_score": 1-10,
  "reason": "short explanation"
}
"""

def classify_scam(description: str):
    prompt = SYSTEM_PROMPT + f"\n\nScam description:\n{description}"

    response = MODEL.generate_content(prompt)
    text = response.text.strip()

    try:
        return json.loads(text)
    except Exception:
        # Fallback safety
        return {
            "scam_type": "OTHER",
            "risk_score": 3,
            "reason": "AI could not classify clearly"
        }
