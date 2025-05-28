def format_question_number(number: int) -> str:
    """Formatta il numero della domanda con un'icona"""
    return f"❓ Domanda {number}:"


def format_progress_text(current: int, total: int) -> str:
    """Formatta il testo del progresso"""
    return f"Progresso: {current}/{total} ({int((current/total)*100)}%)"