import logging
from typing import Any, AsyncGenerator, Dict, Optional
import litellm
from litellm import acompletion, completion
from app.core.config import settings

# Global LiteLLM configuration
# This ensures that unsupported parameters (like response_format in NVIDIA NIM) are dropped
litellm.drop_params = True

logger = logging.getLogger(__name__)

class ModelFactory:
    """
    ModelFactory serves as the LLM Gateway for the application.
    It wraps LiteLLM calls to interact with various providers (Ollama, NVIDIA NIM, etc.).
    """
    
    _current_model: Optional[str] = None
    
    @classmethod
    def setup(cls):
        """Configure LiteLLM settings"""
        litellm.api_base = settings.OLLAMA_API_BASE
        litellm.drop_params = True  # Ensure drop_params is set
        cls._current_model = settings.DEFAULT_MODEL
        
    @classmethod
    def get_current_model(cls) -> str:
        return cls._current_model or settings.DEFAULT_MODEL

    @classmethod
    def set_current_model(cls, model_name: str):
        cls._current_model = model_name
        
    @classmethod
    def get_default_model(cls) -> str:
        return cls.get_current_model()

    @classmethod
    async def generate(
        cls, 
        messages: list[Dict[str, str]], 
        model: Optional[str] = None,
        **kwargs
    ) -> Any:
        """
        Standard async completion call.
        """
        model_name = model or cls.get_default_model()
        
        # Configure provider-specific params
        call_params = {
            "model": model_name,
            "messages": messages,
            **kwargs
        }

        if model_name.startswith("nvidia_nim/"):
            call_params["api_base"] = settings.NVIDIA_API_BASE
            call_params["api_key"] = settings.NVIDIA_API_KEY
        else:
            call_params["api_base"] = settings.OLLAMA_API_BASE

        try:
            response = await acompletion(**call_params)
            return response
        except Exception as e:
            logger.error(f"Error during LLM generation: {str(e)}")
            raise

    @classmethod
    async def stream_generate(
        cls, 
        messages: list[Dict[str, str]], 
        model: Optional[str] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Streaming async completion call.
        """
        model_name = model or cls.get_default_model()
        
        # Configure provider-specific params
        call_params = {
            "model": model_name,
            "messages": messages,
            "stream": True,
            **kwargs
        }

        if model_name.startswith("nvidia_nim/"):
            call_params["api_base"] = settings.NVIDIA_API_BASE
            call_params["api_key"] = settings.NVIDIA_API_KEY
        else:
            call_params["api_base"] = settings.OLLAMA_API_BASE

        try:
            response = await acompletion(**call_params)
            async for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"Error during streaming LLM generation: {str(e)}")
            raise
