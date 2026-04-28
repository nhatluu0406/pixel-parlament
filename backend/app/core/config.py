from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "PixelParlament"
    API_V1_STR: str = "/api/v1"
    
    # Ollama Configuration
    OLLAMA_API_BASE: str = "http://localhost:11434"
    DEFAULT_MODEL: str = "ollama/qwen2.5:1.5b"
    
    # NVIDIA NIM Configuration
    NVIDIA_API_KEY: str = ""
    NVIDIA_API_BASE: str = "https://integrate.api.nvidia.com/v1"
    
    # Database Configuration
    DATABASE_URL: str = "sqlite:///./pixel_parlament.db"
    
    # Storage Configuration
    SOULS_DIR: str = "souls"

    class Config:
        env_file = ".env"

settings = Settings()
