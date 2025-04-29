from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Telegram Bot settings
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    API_ID: str = os.getenv("API_ID", "")
    API_HASH: str = os.getenv("API_HASH", "")
    
    # Database settings
    DATABASE_URL: str = "sqlite:///chat_connector.db"
    
    # Session settings
    SESSION_DIR: str = "sessions"
    
    # Logging settings
    LOG_DIR: str = "logs"
    LOG_LEVEL: str = "INFO"
    
    # Joining settings
    MIN_JOIN_DELAY: int = 10  # seconds
    MAX_JOIN_DELAY: int = 300  # seconds
    DELAY_INCREMENT: float = 0.1  # 10%
    
    # Proxy settings
    USE_PROXY: bool = False
    PROXY_TYPE: Optional[str] = None
    PROXY_HOST: Optional[str] = None
    PROXY_PORT: Optional[int] = None
    PROXY_USERNAME: Optional[str] = None
    PROXY_PASSWORD: Optional[str] = None
    
    class Config:
        env_file = ".env"

settings = Settings() 