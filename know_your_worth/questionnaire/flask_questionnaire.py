from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/start_questionnaire', methods=['GET'])
def start_questionnaire():
    # Example: return the first question
    first_question = {
        "question_id": 1,
        "question_text": "Qual è il tuo nome?"
    }
    return jsonify(first_question)

@app.route('/next_question', methods=['POST'])
def next_question():
    data = request.get_json()
    # Example: get the answer and return the next question
    answer = data.get('answer')
    question_id = data.get('question_id')

    # Dummy logic for demonstration
    if question_id == 1:
        next_q = {
            "question_id": 2,
            "question_text": "Quanti anni hai?"
        }
    else:
        next_q = {
            "message": "Questionario completato!"
        }
    return jsonify(next_q)

if __name__ == '__main__':
    app.run(debug=True)