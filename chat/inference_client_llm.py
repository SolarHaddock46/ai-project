from langchain_core.language_models import LLM
from huggingface_hub import InferenceClient
from typing import Any, Dict, List, Optional

class InferenceClientLLM(LLM):
    """Обёртка для InferenceClient, чтобы использовать его как LLM в LangChain."""
    client: InferenceClient
    model: str
    max_length: int = 512
    temperature: float = 0.7

    def _call(self, prompt: str, stop: Optional[List[str]] = None, **kwargs: Any) -> str:
        """Генерирует текст с использованием InferenceClient."""
        response = self.client.text_generation(
            prompt,
            model=self.model,
            max_new_tokens=self.max_length,
            temperature=self.temperature,
            stop_sequences=stop,
            **kwargs
        )
        return response

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Возвращает параметры для идентификации модели."""
        return {
            "model": self.model,
            "max_length": self.max_length,
            "temperature": self.temperature
        }

    @property
    def _llm_type(self) -> str:
        """Тип LLM."""
        return "inference_client_llm"