import time
import os
import requests
from flask import Flask, request, jsonify

from llm.sonar_llm import SonarClient
from rag.rag_engine import RAGEngine
from questionnaire.questionnaire_refiner import QuestionnaireRefiner
from worker_exploitation_checker.prompts import get_prompt_exploitation_checker, get_prompt_query_rewriting
from advice_generator.prompts import get_prompt_advice_generator


class WorkflowManager:
    def __init__(self,
                 config: dict):
        self.worker_info = {}
        self.config = config
        self.manager_ip = config["manager"]["host"]
        self.manager_port = config["manager"]["port"]
        self.manager_url = f"http://{self.manager_ip}:{self.manager_port}"
        self.flask_questionnaire_ip = config["flask_questionnaire"]["host"]
        self.flask_questionnaire_port = config["flask_questionnaire"]["port"]
        self.flask_questionnaire_url = f"http://{self.flask_questionnaire_ip}:{self.flask_questionnaire_port}"
        self.flask_check_exploitation_ip = config["flask_check_exploitation"]["host"]
        self.flask_check_exploitation_port = config["flask_check_exploitation"]["port"]
        self.flask_check_exploitation_url = f"http://{self.flask_check_exploitation_ip}:{self.flask_check_exploitation_port}"
        self.flask_generate_advice_ip = config["flask_advice_generator"]["host"]
        self.flask_generate_advice_port = config["flask_advice_generator"]["port"]
        self.flask_generate_advice_url = f"http://{self.flask_generate_advice_ip}:{self.flask_generate_advice_port}"
        self._init_llm_clients()
        self.questionnaire_refiner = QuestionnaireRefiner(llm_client=self.sonar_client)

    def _init_components(self):
        # Inizializza i componenti necessari, come il client LLM e il motore RAG
        self._init_llm_clients()
        self.rag_engine_exploitation_checker = RAGEngine(
            db_dir="./index/ccnl",
            collection_name="ccnl",
            llm_api_key=os.getenv("SONAR_API_KEY"),
            llm_model=os.getenv("SONAR_API_MODEL"),
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )

    def _init_llm_clients(self):
        self.sonar_client = SonarClient(api_key=os.getenv("SONAR_API_KEY"),
                                        model=os.getenv("SONAR_API_MODEL"))

    def run(self):
        # Simulazione: avvia il workflow
        questionnaire_schema = self.get_questionnaire()
        worker_answers = self.simulate_completion_questionnaire(questionnaire_schema)
        refinement_data = self.refine_questionnaire(questionnaire_schema, worker_answers)  # TODO: attualmente solo una volta lo fa, in futuro possiamo farlo più volte
        print("refinement_data", refinement_data)
        follow_up_questions = refinement_data.get("follow_up_questions")
        follow_up_answers = refinement_data.get("follow_up_answers")
        if refinement_data.get("status") == "incomplete" and follow_up_questions and follow_up_answers:
            print("Follow up questions:", follow_up_questions)
            print("Follow up answers:", follow_up_answers)
            # Ad esempio, potresti aggiornare worker_info o fare ulteriori chiamate
        query_for_check_worker_exploitation = self.get_query_for_check_worker_exploitation(questionnaire_schema,
                                                                                           worker_answers,
                                                                                           follow_up_questions,
                                                                                           follow_up_answers)
        print("Query for check worker exploitation:", query_for_check_worker_exploitation)
        exploiment_worker_information = self.check_worker_exploitation(questionnaire_schema,
                                                                        worker_answers,
                                                                        follow_up_questions,
                                                                        follow_up_answers)
        print(f"exploiment_worker_information: {exploiment_worker_information}")
        generated_advice = self.generate_advice(questionnaire_schema,
                                                worker_answers,
                                                follow_up_questions,
                                                follow_up_answers,
                                                exploiment_worker_information)
        print("generated_advice:", generated_advice)
        return {"status": "completed", "worker_info": self.worker_info}
    
    def elaborate(self,
                  questionnaire_schema: dict,
                  worker_answers: dict,
                  follow_up_questions: list,
                  follow_up_answers: list):
        # DA IMPLEMENTARE, vedi run
        query_for_check_worker_exploitation = self.get_query_for_check_worker_exploitation(questionnaire_schema,
                                                                                           worker_answers,
                                                                                           follow_up_questions,
                                                                                           follow_up_answers)
        print("Query for check worker exploitation:", query_for_check_worker_exploitation)
        exploiment_worker_information = self.check_worker_exploitation(questionnaire_schema,
                                                                        worker_answers,
                                                                        follow_up_questions,
                                                                        follow_up_answers)
        print(f"exploiment_worker_information: {exploiment_worker_information}")
        generated_advice = self.generate_advice(questionnaire_schema,
                                                worker_answers,
                                                follow_up_questions,
                                                follow_up_answers,
                                                exploiment_worker_information)
        print("generated_advice:", generated_advice)
        return {
            "status": "completed",
            "worker_info": self.worker_info,
            "generated_advice": generated_advice}

    def get_questionnaire(self):
        url = f"{self.flask_questionnaire_url}/get_questionnaire"
        print(f"Chiamata a: {url}")
        response = requests.get(url)
        try:
            questionnaire_schema = response.json()
            return questionnaire_schema
        except Exception as e:
            print("Errore durante il parsing JSON:", e)
            return {"error": str(e)}

    def refine_questionnaire(self, questionnaire: dict, user_answers: dict) -> dict:
        print("Refining questionnaire...")
        data = self.questionnaire_refiner.refine(questionnaire, user_answers)
        return data

    def get_query_for_check_worker_exploitation(self,
                                                questionnaire_schema: dict,
                                                worker_answers: dict,
                                                follow_up_questions: list,
                                                follow_up_answers: list):
        print("Query rewriting through LLM..")
        try:
            # Generazione del prompt
            prompt = get_prompt_query_rewriting(
                questionnaire_schema,
                worker_answers,
                follow_up_questions,
                follow_up_answers
            )
            # Chiamata al client LLM
            response = self.sonar_client.ask(prompt)
            # Estrazione del contenuto dalla risposta
            rewritten_query = ""
            # Gestione di diversi tipi di risposta
            if isinstance(response, str):
                rewritten_query = response
            elif hasattr(response, 'choices') and response.choices:
                rewritten_query = response.choices[0].message.content
            elif hasattr(response, 'content'):
                rewritten_query = response.content
            elif hasattr(response, 'message') and hasattr(response.message, 'content'):
                rewritten_query = response.message.content
            else:
                # Fallback: converti in stringa
                rewritten_query = str(response)
            return jsonify({"rewritten_query": rewritten_query})
        except Exception as e:
            print(f"⚠️ Errore durante la chiamata a llm.ask: {str(e)}")
            print(f"🔍 Tipo di errore: {type(e)}")
            # Restituisci un JSON di errore con status code appropriato
            return jsonify({"error": str(e)}), 500

    def is_worker_info_complete(self):
        return all(value is not None for value in self.worker_info.values())

    def refine_worker_info(self):
        for key, value in self.worker_info.items():
            if value is None:
                self.worker_info[key] = "da compilare"

    def check_worker_exploitation(self,
                                  questionnaire_schema: dict,
                                  worker_answers: dict,
                                  follow_up_questions: list,
                                  follow_up_answers: list):
        print("Controllo sfruttamento lavoratore...")
        prompt = get_prompt_exploitation_checker(
                questionnaire_schema,
                worker_answers,
                follow_up_questions,
                follow_up_answers
            )
        try:
            result = self.rag_engine_exploitation_checker.query(prompt=prompt)
            print(f"result: {result} - type: {type(result)}")
            # Estrai il testo della risposta
            if hasattr(result, 'response'):
                response_text = str(result.response)
            else:
                response_text = str(result)
            return jsonify({"result": response_text}), 200
        except Exception as e:
            print(f"Errore durante la query: {e}")
            return jsonify({"error": "Errore interno del server"}), 500
        
    def generate_advice(self,
                        questionnaire_schema: dict,
                        worker_answers: dict,
                        follow_up_questions: list,
                        follow_up_answers: list,
                        exploiment_worker_information: str
                        ):
        try:
            print("Sto valutando come consigliare il lavoratore...")
            prompt = get_prompt_advice_generator(
                questionnaire_schema,
                worker_answers,
                follow_up_questions,
                follow_up_answers,
                exploiment_worker_information
            )
            # Chiamata al client LLM
            response = self.sonar_client.ask(prompt)
            # Estrazione del contenuto dalla risposta
            advice = ""
            # Gestione di diversi tipi di risposta
            if isinstance(response, str):
                advice = response
            elif hasattr(response, 'choices') and response.choices:
                advice = response.choices[0].message.content
            elif hasattr(response, 'content'):
                advice = response.content
            elif hasattr(response, 'message') and hasattr(response.message, 'content'):
                advice = response.message.content
            else:
                # Fallback: converti in stringa
                advice = str(response)
            return jsonify({"advice": advice})
        except Exception as e:
            print(f"⚠️ Errore durante la chiamata a llm.ask: {str(e)}")
            print(f"🔍 Tipo di errore: {type(e)}")
            # Restituisci un JSON di errore con status code appropriato
            return jsonify({"error": str(e)}), 500