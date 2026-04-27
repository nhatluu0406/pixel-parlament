from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "PixelParlament"
    API_V1_STR: str = "/api/v1"
    
    # Ollama Configuration
    OLLAMA_API_BASE: str = "http://localhost:11434"
    DEFAULT_MODEL: str = "ollama/qwen2.5:1.5b"
    
    # Database Configuration
    DATABASE_URL: str = "sqlite:///./pixel_parlament.db"
    
    # Storage Configuration
    SOULS_DIR: str = "souls"

    class Config:
        env_file = ".env"

settings = Settings()
