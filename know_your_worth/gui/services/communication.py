import requests
import streamlit as st
from typing import List, Dict, Optional

class APIService:
    """Servizio per gestire le chiamate API al backend Flask"""
    
    def __init__(self):
        # Configura l'URL base dal file di configurazione o variabili d'ambiente
        self.base_url = self._get_base_url()
        self.timeout = 30
    
    def _get_base_url(self) -> str:
        """Ottiene l'URL base del backend"""
        # Puoi configurare questo tramite st.secrets o variabili d'ambiente
        try:
            return st.secrets.get("BACKEND_URL", "http://localhost:5001")
        except:
            return "http://localhost:5001"
    
    def get_questionnaire(self) -> Optional[Dict]:
        """Ottiene le domande del questionario dal backend"""
        try:
            response = requests.get(
                f"{self.base_url}/get_questionnaire",
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                return response.json()  # Restituisce l'intero JSON con "questions"
            else:
                st.error(f"Errore del server: {response.status_code}")
                return None
                
        except requests.exceptions.ConnectionError:
            st.error("🔌 Impossibile connettersi al server. Verifica che il backend sia attivo.")
            return None
        except requests.exceptions.Timeout:
            st.error("⏱️ Timeout della richiesta. Il server potrebbe essere sovraccarico.")
            return None
        except Exception as e:
            st.error(f"Errore imprevisto: {str(e)}")
            return None
    
    def submit_answers(self, answers: Dict) -> bool:
        """Invia le risposte al backend"""
        try:
            response = requests.post(
                f"{self.base_url}/api/submit-answers",
                json={"answers": answers},
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
            
            return response.status_code == 200
            
        except Exception as e:
            st.error(f"Errore nell'invio: {str(e)}")
            return False
