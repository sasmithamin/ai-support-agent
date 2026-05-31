# settings.py - Correct way ✅
import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

# Load .env file
load_dotenv()

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
    
    # Database  reads from .env
    database_url: str = os.getenv("DATABASE_URL", "")
    
    # Vector Database 
    chroma_db_path: str = os.getenv("CHROMA_DB_PATH", "./data/chroma_db")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    
    # LLM Configuration 
    use_local_llm: bool = os.getenv("USE_LOCAL_LLM", "True").lower() == "true"
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    
    # Cloud LLMs 
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    
    google_api_key: Optional[str] = os.getenv("GOOGLE_API_KEY")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
    
    anthropic_api_key: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    claude_model: str = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")
    
    # External APIs 
    tavily_api_key: Optional[str] = os.getenv("TAVILY_API_KEY")
    serper_api_key: Optional[str] = os.getenv("SERPER_API_KEY")
    
    # Slack 
    slack_bot_token: Optional[str] = os.getenv("SLACK_BOT_TOKEN")
    slack_signing_secret: Optional[str] = os.getenv("SLACK_SIGNING_SECRET")
    slack_channel_id: Optional[str] = os.getenv("SLACK_CHANNEL_ID")
    
    # Agent Configuration 
    max_iterations: int = int(os.getenv("MAX_ITERATIONS", "10"))
    agent_timeout: int = int(os.getenv("AGENT_TIMEOUT", "120"))
    enable_sentiment_analysis: bool = os.getenv("ENABLE_SENTIMENT_ANALYSIS", "True").lower() == "true"
    auto_escalation_threshold: float = float(os.getenv("AUTO_ESCALATION_THRESHOLD", "0.3"))
    
    # RAG Configuration 
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "1000"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    similarity_top_k: int = int(os.getenv("SIMILARITY_TOP_K", "5"))
    similarity_threshold: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.7"))
    
    # Logging 
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: str = os.getenv("LOG_FILE", "./logs/support_agent.log")


# Global settings instance
settings = Settings()