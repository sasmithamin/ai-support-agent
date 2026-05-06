from langchain_ollama import ChatOllama
from config.settings import settings


def get_llm(temperature: float = 0.7):
    """Factory function to get the configured LLM"""
    
    if settings.use_local_llm:
        # Local Ollama
        return ChatOllama(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
            temperature=temperature,
        )
    
#    elif settings.openai_api_key:
        # OpenAI
        return ChatOpenAI(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            temperature=temperature,
        )
    
#    elif settings.google_api_key:
        # Google Gemini
        return ChatGoogleGenerativeAI(
            google_api_key=settings.google_api_key,
            model=settings.gemini_model,
            temperature=temperature,
        )
    
#    elif settings.anthropic_api_key:
        # Anthropic Claude
        return ChatAnthropic(
            anthropic_api_key=settings.anthropic_api_key,
            model=settings.claude_model,
            temperature=temperature,
        )
    
    else:
        raise ValueError("No LLM configured. Please set up Ollama or provide API keys.")