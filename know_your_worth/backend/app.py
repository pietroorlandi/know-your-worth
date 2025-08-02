import time
import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.exceptions import BadRequest

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


@app.route("/handle_conversation_for_more_information", methods=["POST"])
def handle_conversation_for_more_information():
    try:
        data = request.get_json(force=True)

        # form_data = data.get("form_data")  # Dati iniziali o aggregati
        # questionnaire_schema = data.get("questionnaire_schema")
        user_answers = data.get("user_answers")
        conversation_history = data.get("conversation_history", [])  # Lista di dict con {role, content}

        print("Received data for handle_conversation_for_more_information:")
        # print(f"Questionnaire Schema: {questionnaire_schema}")
        print(f"User Answers: {user_answers}")
        print(f"Conversation History: {conversation_history}")
        # if not form_data:
        #     raise BadRequest("Missing 'form_data' in request")
        # form_data = {
        #     "questionnaire_schema": questionnaire_schema,
        #     "worker_answers": user_answers
        # }

        # Passa i dati al manager che gestisce la logica con il LLM
        result = manager.handle_conversation_for_more_info(user_answers, conversation_history)

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

@app.route("/handle_message", methods=["POST"])
def handle_message():
    data = request.get_json()
    sender = data.get("sender")
    messages = data.get("messages")
    if not sender or not messages:
        return jsonify({"error": "Missing data"}), 400
    try:
        result = manager.handle_message(sender, messages)  #  LLM vede se mancano informazioni e nel caso 
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
