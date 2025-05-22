import requests
from know_your_worth.llm.llm import LLMClient


class SonarClient(LLMClient):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.endpoint = "https://api.perplexity.ai/sonar"  # fittizio

    def ask(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        body = {
            "model": "sonar-small-chat",  # o altro
            "messages": [{"role": "user", "content": prompt}]
        }

        response = requests.post(self.endpoint, json=body, headers=headers)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
