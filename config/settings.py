from pydantic import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = False
    api_reload: bool = False
    
    # AI Model Configuration
    openai_api_key: str
    anthropic_api_key: Optional[str] = None
    huggingface_api_key: Optional[str] = None
    default_model: str = "gpt-3.5-turbo"
    embedding_model: str = "text-embedding-ada-002"
    
    # Database Configuration
    database_url: str = "postgresql://username:password@localhost:5432/sdg_rag_db"
    redis_url: str = "redis://localhost:6379/0"
    
    # Vector Database
    chroma_db_path: str = "./data/chroma"
    chroma_host: str = "localhost"
    chroma_port: int = 8000
    
    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # External API Keys
    uber_api_key: Optional[str] = None
    grab_api_key: Optional[str] = None
    tfl_api_key: Optional[str] = None
    smartcar_client_id: Optional[str] = None
    smartcar_client_secret: Optional[str] = None
    open_charge_map_api_key: Optional[str] = None
    
    # UN/SDG APIs
    un_data_api_key: Optional[str] = None
    un_habitat_api_key: Optional[str] = None
    world_bank_api_key: Optional[str] = None
    
    # File Processing
    max_file_size: str = "100MB"
    supported_formats: List[str] = ["pdf", "docx", "txt", "md", "pptx"]
    upload_dir: str = "./data/uploads"
    processed_dir: str = "./data/processed"
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    log_file: str = "./logs/app.log"
    
    # Monitoring
    prometheus_port: int = 9090
    metrics_enabled: bool = True
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    rate_limit_burst: int = 10
    
    # Caching
    cache_ttl: int = 3600
    cache_max_size: int = 1000
    
    # Background Tasks
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

# Ensure directories exist
os.makedirs(settings.upload_dir, exist_ok=True)
os.makedirs(settings.processed_dir, exist_ok=True)
os.makedirs(settings.chroma_db_path, exist_ok=True)
os.makedirs(os.path.dirname(settings.log_file), exist_ok=True)