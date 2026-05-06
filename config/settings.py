from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False
    )
    
    # Application
    app_name: str = "AI Support Agent"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database
    database_url: str = "sqlite+aiosqlite:///./data/support_agent.db"
    
    # Vector Database
    chroma_db_path: str = "./data/chroma_db"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # LLM Configuration
    use_local_llm: bool = True
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"
    
    
    
    # External APIs
    tavily_api_key: Optional[str] = None
    serper_api_key: Optional[str] = None
    
    # Slack
    slack_bot_token: Optional[str] = None
    slack_signing_secret: Optional[str] = None
    slack_channel_id: Optional[str] = None
    
    # Agent Configuration
    max_iterations: int = 10
    agent_timeout: int = 120
    enable_sentiment_analysis: bool = True
    auto_escalation_threshold: float = 0.3
    
    # RAG Configuration
    chunk_size: int = 1000
    chunk_overlap: int = 200
    similarity_top_k: int = 5
    similarity_threshold: float = 0.7
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "./logs/support_agent.log"


# Global settings instance
settings = Settings()