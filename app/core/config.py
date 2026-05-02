import os
from dotenv import load_dotenv

# 🔥 Load .env file
load_dotenv()

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL")
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS = 24

    def validate(self):
        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL is not set")

settings = Settings()
settings.validate()