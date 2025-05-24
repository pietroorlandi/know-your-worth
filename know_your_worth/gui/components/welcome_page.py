import streamlit as st

def show_welcome_page():
    """Mostra la pagina di benvenuto"""
    
    # Header con styling
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="color: #2E86C1; font-size: 3rem; margin-bottom: 1rem;">
            ⚖️ Conosci i Tuoi Diritti
        </h1>
        <h3 style="color: #5D6D7E; font-weight: 300; margin-bottom: 2rem;">
            Verifica se i tuoi diritti sul lavoro sono rispettati
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Contenuto principale
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        ### Come funziona?
        
        Questo strumento ti aiuta a capire se i tuoi diritti come lavoratore vengono rispettati.
        
        **Il processo è semplice:**
        1. 📝 Rispondi a un questionario di pochi minuti
        2. 🔍 Confrontiamo le tue risposte con i CCNL vigenti
        3. 📊 Ricevi un'analisi dettagliata della tua situazione
        4. 💡 Ottieni consigli su come procedere
        
        ---
        
        ### Perché è importante?
        
        - ✅ **Trasparenza**: Comprendi i tuoi diritti
        - 🛡️ **Protezione**: Individua possibili violazioni
        - 📋 **Informazione**: Conosci i contratti collettivi
        - 🤝 **Supporto**: Ricevi consigli personalizzati
        
        ---
        """)
        
        # Pulsante per iniziare
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button(
            "🚀 Inizia il Questionario",
            type="primary",
            use_container_width=True,
            help="Clicca per iniziare la valutazione dei tuoi diritti"
        ):
            st.session_state.current_page = "questionnaire"
            st.rerun()
    
    # Footer
    st.markdown("""
    ---
    <div style="text-align: center; color: #7F8C8D; font-size: 0.9rem;">
        <p>🔒 Le tue informazioni sono trattate in modo confidenziale</p>
        <p>📞 Per supporto o domande, contatta il nostro team</p>
    </div>
    """, unsafe_allow_html=True)