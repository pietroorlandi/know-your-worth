from flask import Flask, request, jsonify
import os

from know_your_worth.rag.rag_engine import RAGEngine
from know_your_worth.llm.sonar_llm import SonarClient
from know_your_worth.utils.os_utils import read_yaml_file
from prompts import get_prompt_advice_generator


app = Flask(__name__)
llm_client = SonarClient(
    api_key=os.getenv("SONAR_API_KEY"),
    model=os.getenv("SONAR_API_MODEL")
)


@app.route('/generate_advice', methods=['POST'])
def generate_advice():
    try:
        data = request.get_json()
        # Validazione dei dati di input
        if not data:
            return jsonify({"error": "Nessun dato JSON fornito"}), 400
        questionnaire_schema = data.get("questionnaire_schema")
        worker_answers = data.get("worker_answers")
        follow_up_questions = data.get("follow_up_questions")
        follow_up_answers = data.get("follow_up_answers")
        exploiment_worker_information = data.get("exploiment_worker_information")
        # Generazione del prompt
        prompt = get_prompt_advice_generator(
            questionnaire_schema,
            worker_answers,
            follow_up_questions,
            follow_up_answers,
            exploiment_worker_information
        )
        # Chiamata al client LLM
        response = llm_client.ask(prompt)
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
    

config = read_yaml_file("configs.yaml")

if __name__ == '__main__':
    app.run(debug=True, host=config["flask_advice_generator"]["host"], port=config["flask_advice_generator"]["port"])