import instructor
from openai import OpenAI
from pydantic import BaseModel

from .llm import LLMClient


class SonarClient(LLMClient):
    def __init__(self,
                 api_key: str,
                 model: str):
        self.api_key = api_key
        self.model = model
        self.endpoint = 'https://api.perplexity.ai'
        self.client = instructor.from_perplexity(OpenAI(api_key=self.api_key, base_url=self.endpoint))

    def ask(self, prompt: str, response_model=None) -> str:
        # chat completion without streaming
        messages = [
            {"role": "system", "content": 'Sei un Assistente AI esperto di diritto del lavoro italiano.'},
            {"role": "user", "content": prompt}
        ]
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_model=response_model
        )
        return response