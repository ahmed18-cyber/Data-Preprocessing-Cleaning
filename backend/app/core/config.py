"""Application configuration settings."""
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application runtime settings loaded from environment or .env file."""
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    MAX_UPLOAD_SIZE_MB: int = 50

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000"

    # Recommendation thresholds
    MISSING_VALUE_THRESHOLD_PERCENT: float = 5.0
    HIGH_CARDINALITY_PERCENT_THRESHOLD: float = 50.0
    SKEWNESS_THRESHOLD: float = 2.0
    OUTLIER_IQR_FACTOR: float = 1.5
    LOW_VARIANCE_THRESHOLD: float = 0.01
    DUPLICATE_ROW_THRESHOLD_PERCENT: float = 5.0

    SESSION_EXPIRY_HOURS: int = 2
    SESSION_CLEANUP_INTERVAL_MINUTES: int = 30
    STORAGE_DIR: str = "storage_data/sessions"

    # Backend base directory
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse comma-separated CORS origins into a trimmed list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def max_upload_size_bytes(self) -> int:
        """Return maximum upload size in bytes."""
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    @property
    def storage_path(self) -> Path:
        """Absolute path to the session storage root directory."""
        path = self.BASE_DIR / self.STORAGE_DIR
        path.mkdir(parents=True, exist_ok=True)
        return path


settings = Settings()

