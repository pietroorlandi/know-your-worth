from typing import Tuple

def validate_answer(answer: str, question: dict) -> Tuple[bool, str]:
    """
    Valida una risposta basandosi sui criteri della domanda
    
    Args:
        answer: La risposta dell'utente
        question: Il dizionario della domanda con i metadati
    
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    
    # Controlla se il campo è obbligatorio
    if question.get('required', False):
        if not answer or answer.strip() == "":
            return False, "⚠️ Questa domanda è obbligatoria"
    
    # Validazioni specifiche basate sul contenuto della domanda
    question_text = question.get('text', '').lower()
    
    # Validazione per età
    if 'anni hai' in question_text or 'età' in question_text:
        if answer.strip():
            try:
                age = int(answer.strip())
                if age < 14 or age > 100:
                    return False, "⚠️ Inserisci un'età valida (14-100 anni)"
            except ValueError:
                return False, "⚠️ Inserisci un numero valido per l'età"
    
    # Validazione per ore di lavoro
    if 'ore lavori' in question_text:
        if answer.strip():
            try:
                hours = float(answer.strip())
                if hours < 0 or hours > 24:
                    return False, "⚠️ Inserisci un numero di ore valido (0-24)"
            except ValueError:
                return False, "⚠️ Inserisci un numero valido per le ore"
    
    # Validazione per giorni della settimana
    if 'giorni alla settimana' in question_text:
        if answer.strip():
            try:
                days = int(answer.strip())
                if days < 0 or days > 7:
                    return False, "⚠️ Inserisci un numero di giorni valido (0-7)"
            except ValueError:
                return False, "⚠️ Inserisci un numero valido per i giorni"
    
    # Validazione lunghezza minima per risposte di testo
    if answer.strip() and len(answer.strip()) < 2:
        return False, "⚠️ La risposta deve contenere almeno 2 caratteri"
    
    return True, ""