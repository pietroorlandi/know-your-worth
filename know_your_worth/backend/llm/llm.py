from abc import ABC, abstractmethod


class LLMClient(ABC):
    @abstractmethod
    def ask(self, prompt: str, response_model=None) -> str:
        pass
