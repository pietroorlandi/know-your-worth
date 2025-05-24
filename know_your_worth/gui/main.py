import streamlit as st
from components.welcome_page import show_welcome_page
from components.questionnaire import show_questionnaire
from services.communication import APIService
from utils.session_state import initialize_session_state

def main():
    st.set_page_config(
        page_title="Diritti del Lavoratore",
        page_icon="⚖️",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Inizializza lo stato della sessione
    initialize_session_state()
    
    # Routing principale
    if st.session_state.current_page == "welcome":
        show_welcome_page()
    elif st.session_state.current_page == "questionnaire":
        show_questionnaire()

if __name__ == "__main__":
    main()