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
        response = self.check_worker_exploitation(
            questionnaire_schema,
            worker_answers,
            follow_up_questions,
            follow_up_answers
        )
        print("Response:", response)
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

    def simulate_completion_questionnaire(self, questionnaire):
        user_answers = {
            "answers": [
                { "question_id": 1, "answer": "Mario" },
                { "question_id": 2, "answer": "30" },
                { "question_id": 3, "answer": "Italia" },
                { "question_id": 4, "answer": "Milano" },
                { "question_id": 5, "answer": "Pulizie" },
                { "question_id": 6, "answer": "3 mesi" },
                { "question_id": 7, "answer": "Sì" },
                { "question_id": 8, "answer": "Agenzia" },
                { "question_id": 9, "answer": "9" },
                { "question_id": 10, "answer": "6" },
                { "question_id": 11, "answer": "07:00 - 17:00" },
                { "question_id": 13, "answer": "900" },
                { "question_id": 14, "answer": "Contanti" },
                { "question_id": 15, "answer": "No"}
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
