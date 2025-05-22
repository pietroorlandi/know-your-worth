from flask import Flask, request, jsonify

from questionnaire import get_next_question, load_questionnaire_schema
from know_your_worth.utils.os_utils import read_yaml_file

app = Flask(__name__)


@app.route('/start_questionnaire', methods=['GET'])
def start_questionnaire():
    schema = load_questionnaire_schema()
    first_q = schema[0]
    return jsonify({
        "question_id": first_q["id"],
        "question_text": first_q["text"]
    })


@app.route('/next_question', methods=['POST'])
def next_question():
    data = request.get_json()
    question_id = data.get("question_id")
    answer = data.get("answer")

    if question_id is None or answer is None:
        return jsonify({"error": "Missing question_id or answer"}), 400

    next_q, status = get_next_question(question_id, answer)
    return jsonify(next_q), status


@app.route('/get_questionnaire', methods=['GET'])
def get_questionnaire():
    schema = load_questionnaire_schema()
    questions = [
        {
            "question_id": q["id"],
            "question_text": q["text"],
            "required": q["required"]
        } for q in schema
    ]
    return jsonify({
        "questions": questions
    }), 200


@app.route('/send_questionnaire', methods=['POST'])
def send_questionnaire():
    data = request.get_json()
    answers = data.get("answers")

    if not answers or not isinstance(answers, list):
        return jsonify({"error": "Missing or invalid 'answers' field. Must be a list."}), 400

    schema = load_questionnaire_schema()
    required_questions = [q for q in schema if q.get("required", False)]
    answered_ids = {a["question_id"] for a in answers if "question_id" in a}

    missing_questions = []
    for question in required_questions:
        if question["id"] not in answered_ids:
            missing_questions.append({
                "question_id": question["id"],
                "question_text": question["text"]
            })

    if missing_questions:
        return jsonify({
            "error": "Questionnaire incomplete. Missing answers to required questions.",
            "missing_questions": missing_questions
        }), 400

    return jsonify({
        "message": "Questionnaire completed successfully!",
        "answers_received": answers
    }), 200


config = read_yaml_file("configs.yaml")

if __name__ == '__main__':
    app.run(debug=True, host=config["flask_questionnaire"]["host"], port=config["flask_questionnaire"]["port"])