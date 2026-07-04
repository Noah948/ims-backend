# core/config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # General settings
    PROJECT_NAME: str = "IMS Backend"
    DATABASE_URL: str = ""
    FRONTEND_URL: str = ""

    # JWT settings
    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Email settings
    EMAIL_USER: str = ""
    EMAIL_PASS: str = ""
    SMTP_SERVER: str = ""
    SMTP_PORT: int = 465

    # Redis settings
    REDIS_HOST: str = ""
    REDIS_PORT: int 
    REDIS_DB: int 
    REDIS_PASSWORD: str | None = None

    # # Razorpay
    # RAZORPAY_KEY_ID: str = ""
    # RAZORPAY_KEY_SECRET: str = ""
    # RAZORPAY_WEBHOOK_SECRET: str = ""

    class Config:
        env_file = ".env"

settings = Settings()
