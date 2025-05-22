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

    def run(self):
        # Simulazione: avvia il workflow
        questionnaire = self.get_questionnaire()
        worker_answers = self.simulate_completion_questionnaire(questionnaire)
        time.sleep(1)
        # refinement_data = self.refine_questionnaire(questionnaire, worker_answers) # TODO: attualmente solo una volta lo fa, in futuro possiamo farlo più volte
        # if refinement_data["status"] == "incomplete":
        #     worker_answers_refinement = self.simulate_completion_questionnaire(questionnaire)
        #     worker_answers = worker_answers['refinement'] = worker_answers_refinement
        # self.module_2()
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

    def module_2(self):
        pass

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
