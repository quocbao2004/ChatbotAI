import os

class Config:
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://postgres:123456@localhost:5432/chatbotai")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "8c6446b37c671576fe8f8b574e6536afc2ec9ffcb7c8a933cf480da0c5c45ac8")

    # Mail config (Gmail example)
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "true").lower() in ["true", "1"]
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "daoquocbao2k04@gmail.com")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "xmzf ccvf fmwj yzsw")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", MAIL_USERNAME)
