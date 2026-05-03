# Firebase is optional — only initialized if the key file exists
import os
from app.core.logger import logger

FIREBASE_AVAILABLE = False

def init_firebase():
    global FIREBASE_AVAILABLE
    cred_path = "/etc/secrets/firebase_key.json"

    if not os.path.exists(cred_path):
        logger.warning("Firebase key not found — Firebase features disabled")
        return

    try:
        import firebase_admin
        from firebase_admin import credentials
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        FIREBASE_AVAILABLE = True
        logger.info("Firebase initialized successfully")
    except Exception as e:
        logger.warning(f"Firebase init failed: {e}")

init_firebase()