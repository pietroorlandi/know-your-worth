import time
import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

from dotenv import load_dotenv

from questionnaire.questionnaire_refiner import QuestionnaireRefiner
from llm.sonar_llm import SonarClient
from manager import WorkflowManager
from utils.os_utils import read_yaml_file
load_dotenv()


config = read_yaml_file("configs.yaml")
app = Flask(__name__)
CORS(app)  # Permette tutte le origini

manager = WorkflowManager(config)


@app.route("/refine_questionnaire", methods=["POST"])
def refine_questionnaire():
    data = request.get_json()
    questionnaire_schema = data.get("questionnaire_schema")
    user_answers = data.get("user_answers")
    if not questionnaire_schema or not user_answers:
        return jsonify({"error": "Missing data"}), 400
    try:
        result = manager.refine_questionnaire(questionnaire_schema, user_answers)
        # Se è un dataclass
        if hasattr(result, "__dict__"):
            return jsonify(result.__dict__)
        # Se è un Pydantic model
        elif hasattr(result, "dict"):
            return jsonify(result.dict())
        # Se è già un dict (es: in caso di errore gestito)
        elif isinstance(result, dict):
            return jsonify(result)
        else:
            return jsonify({"error": "Unexpected result type"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/elaborate_worker_condition', methods=['POST', 'GET'])
def elaborate_worker_condition():
    print("Entrato nel elaborate_worker_condition")
    data = request.get_json()
    questionnaire_schema = data.get("questionnaire_schema")
    worker_answers = data.get("worker_answers")
    follow_up_questions = data.get("follow_up_questions")
    follow_up_answers = data.get("follow_up_answers")
    result = manager.elaborate(
        questionnaire_schema=questionnaire_schema,
        worker_answers=worker_answers,
        follow_up_questions=follow_up_questions,
        follow_up_answers=follow_up_answers
    )
    print("Elaborazione eseguita")
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True, host=manager.manager_ip, port=manager.manager_port)
