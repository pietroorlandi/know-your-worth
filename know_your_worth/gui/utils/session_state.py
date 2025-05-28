import streamlit as st

def initialize_session_state():
    """Inizializza lo stato della sessione con valori di default"""
    
    # Pagina corrente
    if "current_page" not in st.session_state:
        st.session_state.current_page = "welcome"
    
    # Dati del questionario
    if "questions" not in st.session_state:
        st.session_state.questions = []
    
    if "questions_loaded" not in st.session_state:
        st.session_state.questions_loaded = False
    
    if "current_question_index" not in st.session_state:
        st.session_state.current_question_index = 0
    
    # Risposte dell'utente
    if "answers" not in st.session_state:
        st.session_state.answers = {}

def reset_questionnaire_state():
    """Resetta lo stato del questionario"""
    st.session_state.questions = []
    st.session_state.questions_loaded = False
    st.session_state.current_question_index = 0
    st.session_state.answers = {}