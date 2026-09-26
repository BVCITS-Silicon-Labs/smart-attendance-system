from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    database_url: str = "sqlite:///./data/database/attendance.db"

    # SiWG917 / BRD2605A
    device_ip: str = "192.168.1.50"
    device_port: int = 80
    device_api_key: str = "my-student-attendance-bvc@123"

    face_match_threshold: float = 0.45
    timezone: str = "Asia/Kolkata"
    max_photo_mb: int = 2
    demo_mode: bool = False

    model_config = SettingsConfigDict(
        env_file=ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()

DATA_DIR = ROOT / "data"
PHOTO_DIR = DATA_DIR / "photos"
DB_DIR = DATA_DIR / "database"
MODEL_DIR = DATA_DIR / "models"

for p in (PHOTO_DIR, DB_DIR, MODEL_DIR):
    p.mkdir(parents=True, exist_ok=True)
