import logging
from typing import Any, AsyncGenerator, Dict, Optional
import litellm
from litellm import acompletion, completion
from app.core.config import settings

logger = logging.getLogger(__name__)

class ModelFactory:
    """
    ModelFactory serves as the LLM Gateway for the application.
    It wraps LiteLLM calls to interact with the local Ollama instance.
    """
    
    _current_model: Optional[str] = None
    
    @classmethod
    def setup(cls):
        """Configure LiteLLM settings"""
        litellm.api_base = settings.OLLAMA_API_BASE
        litellm.drop_params = True  # Drop unsupported params for the model
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
        try:
            response = await acompletion(
                model=model_name,
                messages=messages,
                api_base=settings.OLLAMA_API_BASE,
                **kwargs
            )
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
        try:
            response = await acompletion(
                model=model_name,
                messages=messages,
                api_base=settings.OLLAMA_API_BASE,
                stream=True,
                **kwargs
            )
            async for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"Error during streaming LLM generation: {str(e)}")
            raise
