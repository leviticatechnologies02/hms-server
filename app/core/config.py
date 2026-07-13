from pydantic_settings import BaseSettings
from typing import Optional, List
from pydantic import field_validator
import os


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Levitica OneHealth"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:6302867927@localhost:5432/levitica_db"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_SESSION_TTL: int = 3600
    
    # JWT
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Password Policy
    PASSWORD_MIN_LENGTH: int = 12
    PASSWORD_REQUIRE_SPECIAL: bool = True
    PASSWORD_REQUIRE_NUMBER: bool = True
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_HISTORY_COUNT: int = 5
    MAX_LOGIN_ATTEMPTS: int = 5
    
    # Security
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_DAY: int = 1000
    HASHING_ALGORITHM: str = "argon2id"
    
    # CORS - Use str type to avoid JSON parsing
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000"
    CORS_CREDENTIALS: bool = True
    
    # Super Admin
    SUPER_ADMIN_EMAIL: str = "admin@levitica.com"
    SUPER_ADMIN_PASSWORD: str = "Admin@123456"
    
    # Email (SMTP)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = "your-email@gmail.com"
    SMTP_PASSWORD: str = "your-app-password"
    SMTP_FROM_EMAIL: str = "noreply@levitica.com"
    
    # AWS S3 / MinIO
    AWS_ACCESS_KEY_ID: str = "your-access-key"
    AWS_SECRET_ACCESS_KEY: str = "your-secret-key"
    AWS_S3_BUCKET: str = "levitica-files"
    AWS_S3_REGION: str = "us-east-1"
    AWS_S3_ENDPOINT_URL: str = "http://localhost:9000"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convert CORS_ORIGINS string to list."""
        if not self.CORS_ORIGINS:
            return ["*"]
        return [url.strip() for url in self.CORS_ORIGINS.split(",") if url.strip()]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields


# Create settings instance
settings = Settings()