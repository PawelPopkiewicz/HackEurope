"""
Configuration management for the backend application.
Handles environment variables, paths, and application settings.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

# Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Load environment variables
env_path = PROJECT_ROOT / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    logger.warning(f"Environment file not found at {env_path}")


class Settings:
    """Application settings from environment variables."""
    
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_DEBUG: bool = os.getenv("API_DEBUG", "False").lower() == "true"
    
    # Gemini/LLM Configuration
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    
    # Data paths
    DATA_DIR: Path = PROJECT_ROOT / "data"
    MITRE_ATTACK_FILE: Path = DATA_DIR / "mitre_attack.json"
    HONEYPOT_LOGS_FILE: Path = DATA_DIR / "honeypot_logs.json"
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE", None)
    
    # CORS - restrict to explicit origins; use "*" only for local dev via env override
    CORS_ORIGINS: list = [
        o.strip()
        for o in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
        if o.strip() and o.strip().startswith(("http://", "https://"))
    ]

    # Rate limiting (M1033 - System Access Control)
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration settings."""
        errors = []
        
        if not cls.GEMINI_API_KEY:
            errors.append("GEMINI_API_KEY or GOOGLE_API_KEY not set")
        
        if not cls.MITRE_ATTACK_FILE.exists():
            errors.append(f"MITRE ATT&CK data file not found: {cls.MITRE_ATTACK_FILE}")
        
        if errors:
            logger.error("Configuration validation failed:")
            for error in errors:
                logger.error(f"  - {error}")
            return False
        
        return True
    
    @classmethod
    def log_config(cls) -> None:
        """Log configuration details (safe version without sensitive data)."""
        logger.info("=== Backend Configuration ===")
        logger.info(f"API: {cls.API_HOST}:{cls.API_PORT}")
        logger.info(f"Debug: {cls.API_DEBUG}")
        logger.info(f"Gemini API Key: {'***' if cls.GEMINI_API_KEY else 'NOT SET'}")
        logger.info(f"Log Level: {cls.LOG_LEVEL}")
        logger.info(f"Data Directory: {cls.DATA_DIR}")
        logger.info(f"CORS Origins: {cls.CORS_ORIGINS}")
        logger.info(f"Rate Limit: {cls.RATE_LIMIT_PER_MINUTE}/minute")
        logger.info("=" * 30)


# Export settings instance
settings = Settings()
