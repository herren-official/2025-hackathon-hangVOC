from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Claude API 설정 (Optional - Claude를 사용하려면 설정)
    claude_api_key: Optional[str] = None
    claude_model: str = "claude-3-haiku-20240307"
    
    # 임베딩 모델 설정 (sentence-transformers 사용)
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # OpenAI 설정 (Optional - OpenAI를 사용하려면 설정)
    openai_api_key: Optional[str] = None
    openai_embedding_model: str = "text-embedding-3-small"
    openai_chat_model: str = "gpt-4o-mini"
    
    # API 제공자 선택 ('claude' 또는 'openai')
    api_provider: str = "openai"  # 기본값은 openai로 설정
    
    # Slack API 설정
    slack_bot_token: Optional[str] = None
    
    chroma_persist_directory: str = "./chroma_db"
    chroma_collection_name: str = "slack_messages"
    
    max_tokens_per_chunk: int = 1000
    search_top_k: int = 10
    
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    class Config:
        env_file = ".env"

settings = Settings()