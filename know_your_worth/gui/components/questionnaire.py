import streamlit as st
from services.communication import APIService
from utils.validation import validate_answer
from utils.formatting import format_question_number

def show_questionnaire():
    """Mostra il questionario dinamico"""
    
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <h2 style="color: #2E86C1;">📝 Questionario sui Diritti del Lavoro</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Controlla se il questionario è completato
    if is_questionnaire_complete():
        st.success("🎉 Questionario completato con successo!")
        st.info("Grazie per aver completato il questionario sui diritti del lavoro.")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🏠 Torna alla Home", use_container_width=True):
                reset_questionnaire()
                st.session_state.current_page = "welcome"
                st.rerun()
        return
    
    # Carica le domande se non sono già in sessione
    if not st.session_state.questions_loaded:
        load_questions()
    
    # Se le domande non sono ancora caricate, mostra loading
    if not st.session_state.questions:
        show_loading_state()
        return
    
    # Renderizza le domande di follow-up se presenti
    if st.session_state.get("show_follow_up", False):
        render_follow_up_questions()
        return
    
    # Mostra il questionario normale
    show_current_question()
    show_navigation_controls()

def load_questions():
    """Carica le domande dal servizio API"""
    try:
        with st.spinner("Caricamento questionario..."):
            api_service = APIService()
            response_data = api_service.get_questionnaire()
            
            if response_data and 'questions' in response_data:
                st.session_state.questions = response_data['questions']
                st.session_state.questions_loaded = True
                st.session_state.current_question_index = 0
                st.success("Questionario caricato con successo!")
            else:
                st.error("Errore nel caricamento delle domande")
                
    except Exception as e:
        st.error(f"Errore di connessione: {str(e)}")
        show_error_state()

def show_loading_state():
    """Mostra lo stato di caricamento"""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info("🔄 Caricamento questionario in corso...")
        if st.button("🔄 Riprova", use_container_width=True):
            st.session_state.questions_loaded = False
            st.rerun()

def show_error_state():
    """Mostra lo stato di errore"""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.error("❌ Impossibile caricare il questionario")
        if st.button("🏠 Torna alla Home", use_container_width=True):
            st.session_state.current_page = "welcome"
            st.rerun()

def show_current_question():
    """Mostra la domanda corrente"""
    current_q = st.session_state.questions[st.session_state.current_question_index]
    
    # Progress bar
    total_questions = len(st.session_state.questions)
    current_index = st.session_state.current_question_index
    progress = (current_index + 1) / total_questions
    
    st.progress(progress, text=f"Domanda {current_index + 1} di {total_questions}")
    
    # Container per la domanda
    with st.container():
        st.markdown(f"""
        <div style="background-color: #F8F9FA; padding: 2rem; border-radius: 10px; margin: 1rem 0;">
            <h3 style="color: #2C3E50; margin-bottom: 1rem;">
                {format_question_number(current_index + 1)} {current_q['question_text']}
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Campo di input per la risposta
        question_id = current_q['question_id']
        answer_key = f"answer_{question_id}"
        current_answer = st.session_state.answers.get(question_id, "")
        
        answer = st.text_input(
            "La tua risposta:",
            value=current_answer,
            key=answer_key,
            placeholder="Scrivi qui la tua risposta...",
            help="Campo obbligatorio" if current_q.get('required', False) else "Campo facoltativo"
        )
        
        # Salva la risposta in session state
        if answer != current_answer:
            st.session_state.answers[question_id] = answer

def show_navigation_controls():
    """Mostra i controlli di navigazione"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.session_state.current_question_index > 0:
            if st.button("⬅️ Precedente", use_container_width=True):
                go_to_previous_question()
    
    with col2:
        # Mostra il pulsante di invio se è l'ultima domanda
        if is_last_question():
            if st.button("📤 Invia Questionario", type="primary", use_container_width=True):
                submit_questionnaire()
        else:
            # Validazione e pulsante successivo
            current_q = st.session_state.questions[st.session_state.current_question_index]
            question_id = current_q['question_id']
            current_answer = st.session_state.answers.get(question_id, "")
            
            is_valid, error_msg = validate_answer(current_answer, current_q)
            
            if not is_valid and error_msg:
                st.error(error_msg)
            
            if st.button("Successivo ➡️", type="primary", use_container_width=True, disabled=not is_valid):
                go_to_next_question()
    
    with col3:
        if st.button("🏠 Home", use_container_width=True):
            if confirm_exit():
                st.session_state.current_page = "welcome"
                st.rerun()

def go_to_previous_question():
    """Vai alla domanda precedente"""
    if st.session_state.current_question_index > 0:
        st.session_state.current_question_index -= 1
        st.rerun()

def go_to_next_question():
    """Vai alla domanda successiva"""
    if st.session_state.current_question_index < len(st.session_state.questions) - 1:
        st.session_state.current_question_index += 1
        st.rerun()


def is_last_question():
    """Controlla se è l'ultima domanda"""
    return st.session_state.current_question_index == len(st.session_state.questions) - 1


def submit_questionnaire():
    """Invia il questionario e gestisce la risposta del refinement"""
    try:
        api_service = APIService()
        
        with st.spinner("Invio questionario..."):
            result = api_service.submit_answers(st.session_state.questions, st.session_state.answers)
            
        # Controlla se c'è stato un errore nella richiesta
        if "error" in result:
            st.error(f"❌ {result['error']}")
            return
            
        # Gestisci la risposta in base al status
        status = result.get("status")
            
        if status == "complete":
            # Questionario completo - mostra successo
            st.success("✅ Questionario completato con successo!")
            st.balloons()
            
            # Salva lo stato di completamento
            st.session_state.questionnaire_complete = True
            
            # Opzionale: mostra un messaggio di completamento
            st.info("🎉 Hai risposto a tutte le domande necessarie!")
            
            # Qui potresti reindirizzare a una pagina di risultati
            # st.switch_page("results")
            
        elif status == "incomplete":
            # Questionario incompleto - mostra domande di follow-up
            follow_up_questions = result.get("follow_up_questions", [])
            
            if follow_up_questions:
                # Salva le domande di follow-up nel session state
                st.session_state.follow_up_questions = follow_up_questions
                st.session_state.show_follow_up = True
                
                st.warning("📝 Sono necessarie alcune informazioni aggiuntive:")
                st.rerun()  # Ricarica per mostrare le domande
                    
            else:
                st.error("❌ Questionario incompleto ma nessuna domanda di follow-up ricevuta")
        
        else:
            st.error(f"❌ Status non riconosciuto: {status}")
            
    except Exception as e:
        st.error(f"Errore: {str(e)}")


def render_follow_up_questions():
    """Renderizza le domande di follow-up se presenti"""
    if st.session_state.get("show_follow_up", False) and "follow_up_questions" in st.session_state:
        follow_up_questions = st.session_state.follow_up_questions
        
        st.markdown("""
        <div style="background-color: #FFF3CD; padding: 1.5rem; border-radius: 10px; margin: 2rem 0; border-left: 4px solid #FF6B6B;">
            <h4 style="color: #856404; margin: 0;">📝 Domande aggiuntive richieste</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Inizializza le risposte di follow-up se non esistono
        if "follow_up_answers" not in st.session_state:
            st.session_state.follow_up_answers = {}
        
        # Crea i campi per le risposte aggiuntive
        for i, question in enumerate(follow_up_questions):
            st.markdown(f"""
            <div style="background-color: #F8F9FA; padding: 1rem; border-radius: 8px; margin: 1rem 0;">
                <h5 style="color: #2C3E50; margin-bottom: 0.5rem;">Domanda {i+1}</h5>
            </div>
            """, unsafe_allow_html=True)
            
            key = f"follow_up_{i}"
            current_value = st.session_state.follow_up_answers.get(key, "")
            
            answer = st.text_area(
                question,
                value=current_value,
                key=f"input_{key}",  # Chiave unica per evitare conflitti
                height=120,
                placeholder="Scrivi qui la tua risposta...",
                help="Campo obbligatorio"
            )
            
            # Aggiorna il session state
            st.session_state.follow_up_answers[key] = answer
        
        # Bottoni di controllo
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("📤 Invia Risposte", type="primary", use_container_width=True):
                # Verifica che tutte le risposte siano state fornite
                all_answered = all(
                    st.session_state.follow_up_answers.get(f"follow_up_{i}", "").strip() 
                    for i in range(len(follow_up_questions))
                )
                
                if all_answered:
                    submit_follow_up_answers()
                else:
                    st.error("⚠️ Per favore, rispondi a tutte le domande prima di inviare.")
        
        with col2:
            if st.button("❌ Annulla", use_container_width=True):
                cleanup_follow_up_state()
                st.rerun()


def submit_follow_up_answers():
    """Invia le risposte alle domande di follow-up"""
    try:
        api_service = APIService()
        follow_up_questions = st.session_state.get("follow_up_questions", [])
        
        # Prepara le risposte aggiuntive
        additional_answers = {}
        for i, question in enumerate(follow_up_questions):
            key = f"follow_up_{i}"
            if key in st.session_state.follow_up_answers:
                additional_answers[question] = st.session_state.follow_up_answers[key]
        
        # Combina le risposte originali con quelle aggiuntive
        all_answers = {**st.session_state.answers, **additional_answers}
        
        with st.spinner("Invio risposte aggiuntive..."):
            result = api_service.submit_answers(st.session_state.questions, all_answers)
        
        # Controlla se c'è stato un errore nella richiesta
        if "error" in result:
            st.error(f"❌ {result['error']}")
            return
            
        status = result.get("status")
            
        if status == "complete":
            st.success("✅ Questionario completato con successo!")
            st.balloons()
            st.session_state.questionnaire_complete = True
            
            # Pulisci le risposte e domande di follow-up
            cleanup_follow_up_state()
            
            # Ricarica la pagina per nascondere le domande di follow-up
            st.rerun()
            
        elif status == "incomplete":
            # Se ancora incompleto, aggiorna con le nuove domande
            new_follow_up_questions = result.get("follow_up_questions", [])
            if new_follow_up_questions:
                st.session_state.follow_up_questions = new_follow_up_questions
                # Resetta le risposte precedenti per le nuove domande
                st.session_state.follow_up_answers = {}
                st.warning("Sono necessarie ancora altre informazioni...")
                st.rerun()
                
    except Exception as e:
        st.error(f"Errore nell'invio delle risposte aggiuntive: {str(e)}")


def cleanup_follow_up_state():
    """Pulisce lo stato delle domande di follow-up"""
    keys_to_remove = [
        "follow_up_questions", 
        "follow_up_answers",
        "show_follow_up"
    ]
    
    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]

# Funzione helper per verificare se il questionario è completo
def is_questionnaire_complete():
    """Verifica se il questionario è stato completato"""
    return st.session_state.get("questionnaire_complete", False)


# Opzionale: funzione per resettare lo stato del questionario
def reset_questionnaire():
    """Resetta lo stato del questionario"""
    keys_to_remove = [
        "questionnaire_complete", 
        "follow_up_questions",
        "follow_up_answers",
        "show_follow_up"
    ]
    
    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]


def confirm_exit():
    """Conferma l'uscita dal questionario"""
    if st.session_state.answers:
        return st.confirm("Sei sicuro di voler uscire? Le risposte non salvate andranno perse.")
    return True