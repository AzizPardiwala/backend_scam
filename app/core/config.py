import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecret_change_in_production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 24
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    def validate(self):
        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL is not set in environment variables")

settings = Settings()
settings.validate()