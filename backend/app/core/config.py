from pydantic_settings import BaseSettings
from pydantic import validator
from typing import Optional, Dict, Any
import os


class Settings(BaseSettings):
    """Configuration globale de l'application"""
    
    # Configuration de la base de données
    DATABASE_URL: Optional[str] = None
    
    # Configuration du serveur
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Configuration de l'environnement
    ENV: str = "development"
    DEBUG: bool = False
    
    # Clés et secrets
    SECRET_KEY: str = os.urandom(32).hex()
    
    # Configuration du modèle
    MODEL_PROVIDER: str = "ollama"
    MODEL_NAME: str = "llama2"
    
    # Configuration de logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        """Configuration de Pydantic"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
    
    @validator("DATABASE_URL", pre=True, always=True)
    def validate_database_url(cls, v: Optional[str]) -> str:
        """Valide et transforme l'URL de la base de données"""
        if v is None:
            # URL par défaut pour SQLite
            return "sqlite:///./keeper.db"
        return v
    
    def get_database_config(self) -> Dict[str, Any]:
        """Retourne la configuration de la base de données"""
        return {
            "url": self.DATABASE_URL,
            "echo": self.DEBUG
        }

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """Convertit DATABASE_URL en URL compatible SQLAlchemy pour les tests asynchrones"""
        if self.DATABASE_URL.startswith("sqlite:///"):
            return f"sqlite+aiosqlite:///{self.DATABASE_URL.split('///')[1]}"
        return self.DATABASE_URL


# Singleton pour la configuration
settings = Settings()
