import json
import os


# Load schema from file (you could cache it in prod)
def load_questionnaire_schema():
    path = 'data/questionnaire/schema.json'
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def get_question_by_id(schema, qid):
    for q in schema:
        if q["id"] == qid:
            return q
    return None


def get_next_question(current_qid, answer=None):
    schema = load_questionnaire_schema()
    current_q = get_question_by_id(schema, current_qid)
    if not current_q:
        return {"error": "Invalid question_id"}, 400

    next_qid = current_q.get("next")
    if next_qid is None:
        return {"message": "Questionario completato!"}, 200

    next_q = get_question_by_id(schema, next_qid)
    if not next_q:
        return {"error": "Errore nel questionario"}, 500

    return {
        "question_id": next_q["id"],
        "question_text": next_q["text"]
    }, 200

