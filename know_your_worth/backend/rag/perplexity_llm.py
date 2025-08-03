from llama_index.core.llms import CustomLLM, CompletionResponse, LLMMetadata
from llama_index.core.llms.callbacks import llm_completion_callback

from typing import Any
import requests


class PerplexityLLM(CustomLLM):
    model_name: str = "sonar-pro"
    api_key: str = ""
    base_url: str = "https://api.perplexity.ai"
    
    def __init__(self, model_name: str = "sonar-pro", api_key: str = "", **kwargs):
        super().__init__()
        self.model_name = model_name
        self.api_key = api_key
    
    @property
    def metadata(self) -> LLMMetadata:
        return LLMMetadata(
            context_window=4096,  # Adjust based on the model
            num_output=1024,
            model_name=self.model_name,
        )
    
    @llm_completion_callback()
    def complete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": kwargs.get("max_tokens", 2048),
            "temperature": kwargs.get("temperature", 0.3)
        }
        
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            return CompletionResponse(text=result["choices"][0]["message"]["content"])
        else:
            raise Exception(f"Perplexity API error: {response.status_code} - {response.text}")
    
    @llm_completion_callback()
    def stream_complete(self, prompt: str, **kwargs: Any):
        # Implement streaming if needed
        pass