from flask import Flask, jsonify
import time
import requests

from know_your_worth.utils.os_utils import read_yaml_file

app = Flask(__name__)


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
        # self.module_3()
        # self.module_4()
        return {"status": "completed", "worker_info": self.worker_info}
    
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
        
    def refine_questionnaire(self, questionnaire: dict, user_answers: dict):
        url = f"{self.flask_questionnaire_url}/refine_questionnaire"
        payload = {
            "questionnaire_schema": questionnaire,
            "user_answers": user_answers
        }
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Errore durante la chiamata a {url}: {e}")
            return {"error": str(e)}
        
    def get_query_for_check_worker_exploitation(self,
                                                questionnaire_schema: dict,
                                                worker_answers: dict,
                                                follow_up_questions: list,
                                                follow_up_answers: list):
        print("Query rewriting through LLM..")
        url = f"{self.flask_check_exploitation_url}/query_rewriting"
        payload = {
            "questionnaire_schema": questionnaire_schema,
            "worker_answers": worker_answers,
            'follow_up_questions': follow_up_questions,
            'follow_up_answers': follow_up_answers
        }
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()

            if "rewritten_query" in data:
                return data["rewritten_query"]
            else:
                print("⚠️ Risposta JSON inattesa dal server:", data)
                return {"error": "Risposta JSON inattesa dal server"}

        except requests.RequestException as e:
            print(f"Errore durante la chiamata a {url}: {e}")
            return {"error": str(e)}

    def simulate_completion_questionnaire(self, questionnaire):
        user_answers = {
            "answers": [
                { "question_id": 1, "answer": "Abdou" },
                { "question_id": 2, "answer": "27" },
                { "question_id": 3, "answer": "Senegal" },
                { "question_id": 4, "answer": "Provincia di Foggia" },
                { "question_id": 5, "answer": "Raccolta pomodori" },
                { "question_id": 6, "answer": "1 anno" },
                { "question_id": 7, "answer": "No" },
                { "question_id": 8, "answer": "Nessuno / a giornata" },
                { "question_id": 9, "answer": "10" },
                { "question_id": 10, "answer": "7" },
                { "question_id": 11, "answer": "06:00 - 17:00" },
                { "question_id": 12, "answer": "1 pausa di 30 minuti" },
                { "question_id": 13, "answer": "700" },
                { "question_id": 14, "answer": "Contanti" },
                { "question_id": 15, "answer": "No" },
                { "question_id": 16, "answer": "Sì, spesso la domenica" },
                { "question_id": 17, "answer": "No" },
                { "question_id": 18, "answer": "Sì, una volta al braccio" },
                { "question_id": 19, "answer": "No, non mi hanno detto nulla" },
                { "question_id": 20, "answer": "Ci trattano male, se parli troppo ti cacciano. Nessun controllo." }
            ]
        }
        return user_answers
    
    def simulate_completion_after_refinement(self, refinement_data: dict):
        pass

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
        url = f"{self.flask_check_exploitation_url}/check_exploitation"
        payload = {
            "questionnaire_schema": questionnaire_schema,
            "worker_answers": worker_answers,
            'follow_up_questions': follow_up_questions,
            'follow_up_answers': follow_up_answers
        }
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Errore durante la chiamata a {url}: {e}")
            return {"error": str(e)}
        
    def generate_advice(self,
                        questionnaire_schema: dict,
                        worker_answers: dict,
                        follow_up_questions: list,
                        follow_up_answers: list,
                        exploiment_worker_information: str
                        ):
        print("Sto valutando come consigliare il lavoratore...")
        url = f"{self.flask_generate_advice_url}/generate_advice"
        payload = {
            "questionnaire_schema": questionnaire_schema,
            "worker_answers": worker_answers,
            'follow_up_questions': follow_up_questions,
            'follow_up_answers': follow_up_answers,
            "exploiment_worker_information": exploiment_worker_information
        }
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Errore durante la chiamata a {url}: {e}")
            return {"error": str(e)}

    def module_3(self):
        pass

    def module_4(self):
        pass


config = read_yaml_file("configs.yaml")
manager = WorkflowManager(config)


@app.route('/run', methods=['POST', 'GET'])
def run_workflow():
    result = manager.run()
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host=manager.manager_ip, port=manager.manager_port)
