from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    APP_NAME: str = "Nadakki SaaS"
    APP_VERSION: str = "1.0.0"
    ENV: str = "development"
    
    DATABASE_URL: str = "sqlite:///./nadakki.db"
    SQLALCHEMY_ECHO: bool = False
    
    JWT_SECRET_KEY: str = "your-super-secret-key-min-32-chars-change-in-prod"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    STRIPE_SECRET_KEY: str = "sk_test_your_key"
    STRIPE_WEBHOOK_SECRET: str = "whsec_your_secret"
    STRIPE_STARTER_PRICE_ID: str = "price_1234"
    STRIPE_PROFESSIONAL_PRICE_ID: str = "price_5678"
    STRIPE_ENTERPRISE_PRICE_ID: str = "price_9999"
    
    ENCRYPTION_MASTER_KEY: str = "your-32-char-encryption-key"
    REDIS_URL: str = "redis://localhost:6379"
    
    LOG_LEVEL: str = "INFO"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"

settings = Settings()
