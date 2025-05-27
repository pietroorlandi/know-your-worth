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
    
    # Carica le domande se non sono già in sessione
    if not st.session_state.questions_loaded:
        load_questions()
    
    # Se le domande non sono ancora caricate, mostra loading
    if not st.session_state.questions:
        show_loading_state()
        return
    
    # Mostra la domanda corrente
    show_current_question()
    
    # Mostra i controlli di navigazione
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
    """Invia il questionario"""
    try:
        api_service = APIService()
        
        with st.spinner("Invio questionario..."):
            result = api_service.submit_answers(st.session_state.questions, st.session_state.answers)
            
        if result:
            st.success("✅ Questionario inviato con successo!")
            st.balloons()
            # Qui potresti reindirizzare a una pagina di risultati
        else:
            st.error("❌ Errore nell'invio del questionario")
            
    except Exception as e:
        st.error(f"Errore: {str(e)}")

def confirm_exit():
    """Conferma l'uscita dal questionario"""
    if st.session_state.answers:
        return st.confirm("Sei sicuro di voler uscire? Le risposte non salvate andranno perse.")
    return True