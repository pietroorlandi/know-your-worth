import json
from pydantic import BaseModel, Field
from typing import List, Union, Literal
import traceback


class CompleteResponse(BaseModel):
    status: Literal["complete"]


class IncompleteResponse(BaseModel):
    status: Literal["incomplete"]
    follow_up_questions: List[str] = Field(..., max_items=3)


FollowUpResponse = Union[CompleteResponse, IncompleteResponse]


class Interviewer:
    def __init__(self, llm_client):
        self.llm = llm_client
    
    def ask(self, questionnaire_schema: dict, user_answers: dict, conversation: list[str]) -> dict:
        # structured_answers = {
        #     str(ans["question_id"]): ans["answer"]
        #     for ans in user_answers.get("answers", [])
        # }
        prompt = f"""
        Sei un assistente esperto di diritto del lavoro italiano.
        
        Il tuo compito è aiutare un sistema automatico a stabilire se un lavoratore è sfruttato, guidandolo con domande semplici e concrete, senza ripetizioni inutili.
        Considera che il lavoratore non ha competenze legali e potrebbe non comprendere termini complessi.
        
        🔢 Ecco le domande del questionario originale:
        
        {questionnaire_schema}
        
        ed ecco le risposte fornite dall'utente: {user_answers}
        
        🧠 Ecco la conversazione tenuta fino ad ora tra LLM e utente:
        
        {conversation}
        
        📌 Il tuo compito è:
        
        1. Valutare se le risposte raccolte sono sufficienti per stabilire se il lavoratore è sfruttato.
        2. Se servono ulteriori informazioni, proponi FINO A 3 nuove domande, semplici e chiare, che NON siano già presenti né nel questionario iniziale né nei precedenti follow-up.
        
        📤 Rispondi **solo** in uno di questi due formati JSON:
        
        - Caso completo:
        ```json
        {{ "status": "complete" }}
        ```
        
        - Caso incompleto:
        ```json
        {{ "status": "incomplete", "follow_up_questions": ["Domanda 1", "Domanda 2", "Domanda 3"] }}
        ```
        """
        
        try:
            response = self.llm.ask(prompt, response_model=FollowUpResponse)
            return response
        except Exception as e:
            print("⚠️ Errore durante la chiamata a llm.ask:")
            traceback.print_exc()
            return {"error": str(e)}