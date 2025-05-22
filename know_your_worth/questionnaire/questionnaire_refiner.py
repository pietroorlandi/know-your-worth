import json
from pydantic import BaseModel, Field
from typing import List, Union, Literal


class CompleteResponse(BaseModel):
    status: Literal["complete"]


class IncompleteResponse(BaseModel):
    status: Literal["incomplete"]
    follow_up_questions: List[str] = Field(..., max_items=3)


FollowUpResponse = Union[CompleteResponse, IncompleteResponse]


class QuestionnaireRefiner:
    def __init__(self, llm_client):
        self.llm = llm_client

    def refine(self, 
               questionnaire_schema: dict,
               user_answers: dict) -> dict:
        structured = {str(ans["question_id"]): ans["answer"] for ans in user_answers}
        prompt = f"""
        Sei un assistente esperto di diritto del lavoro italiano. 
        Il tuo compito è aiutare un sistema automatico a capire se un lavoratore è sfruttato.

        Il sistema ha sottoposto all’utente un questionario con 20 domande. Ecco le domande originali:

        {json.dumps(questionnaire_schema, indent=2)}

        L’utente ha risposto solo ad alcune di queste domande. Ecco le risposte ricevute:

        {json.dumps(structured, indent=2)}

        📌 **Il tuo compito** è:
        1. Valutare se le risposte sono **sufficienti e chiare** per stabilire se il lavoratore è sfruttato
        2. Se servono più dati, suggerisci **fino a 3 domande** aggiuntive, usando un linguaggio semplice e concreto
        3. NON ripetere domande già presenti nel questionario

        ✉️ Rispondi solo in JSON, in uno di questi due formati:

        - Caso completo:
        {{ "status": "complete" }}

        - Caso incompleto:
        {{ "status": "incomplete", "follow_up_questions": ["Domanda 1", "Domanda 2", "Domanda 3"] }}
        """
        try:
            response = self.llm.ask(prompt, response_model=FollowUpResponse)
            # result = json.loads(response)
            return response
        except Exception as e:
            return {"error": str(e)}



# if __name__ == "__main__":
#     import os
#     import requests
#     from know_your_worth.llm.sonar_llm import SonarClient

#     sonar_llm = SonarClient(api_key=os.getenv("SONAR_API_KEY"),
#                             model=os.getenv("SONAR_API_MODEL"))
#     questionnaire_refiner = QuestionnaireRefiner(llm_client=sonar_llm)
#     # Assumendo che il server Flask sia in esecuzione su localhost:5000
#     BASE_URL = "http://localhost:5000"

#     # Ottieni lo schema del questionario dal server Flask
#     response = requests.get(f"{BASE_URL}/get_questionnaire")
#     questionnaire_schema = response.json()

#     # Ottieni le risposte utente dal server Flask
#     # response = requests.get(f"{BASE_URL}/questionnaire/user_answers")
#     # user_answers = response.json()
#     user_answers = {
#         "answers": [
#             { "question_id": 1, "answer": "Mario" },
#             { "question_id": 2, "answer": "30" },
#             { "question_id": 3, "answer": "Italia" },
#             { "question_id": 4, "answer": "Milano" },
#             { "question_id": 5, "answer": "Pulizie" },
#             { "question_id": 6, "answer": "3 mesi" },
#             { "question_id": 7, "answer": "Sì" },
#             { "question_id": 8, "answer": "Agenzia" },
#             { "question_id": 9, "answer": "9" },
#             { "question_id": 10, "answer": "6" },
#             { "question_id": 11, "answer": "07:00 - 17:00" },
#             { "question_id": 13, "answer": "900" },
#             { "question_id": 14, "answer": "Contanti" },
#             { "question_id": 15, "answer": "No"}
#         ]
#         }

#     response = questionnaire_refiner.refine(questionnaire_schema["questions"], user_answers["answers"])
#     print(response)
