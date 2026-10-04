from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    app_name: str = "FitBuddy – AI Fitness Plan Generator"
    database_url: str = "sqlite:///./fitbuddy.db"
    gemini_api_key: str = ""
    workout_model: str = "gemini-3.8-flash"
    nutrition_model: str = "gemini-3.8-flash"
    admin_password: str = "admin123"
    allow_ai_fallback: bool = True

    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
