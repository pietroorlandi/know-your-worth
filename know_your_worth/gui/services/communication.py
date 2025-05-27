import requests
import os
import streamlit as st
from typing import List, Dict, Optional

from know_your_worth.utils.os_utils import read_yaml_file


class APIService:
    """Servizio per gestire le chiamate API al backend Flask"""
    
    def __init__(self):
        # Configura l'URL base dal file di configurazione o variabili d'ambiente
        self.base_url_questionnaire_flask = self._get_base_url_questionnaire_flask()
        self.base_url_manager = self._get_base_url_manager_flask()
        self.timeout = 90

    def _get_base_url_manager_flask(self) -> str:
        """Ottiene l'URL base del backend"""
        config = read_yaml_file("configs.yaml")
        try:
            return f"http://{config['manager']['ip']}:{config['manager']['port']}"
        except:
            return "http://localhost:5000"
    
    def _get_base_url_questionnaire_flask(self) -> str:
        """Ottiene l'URL base del backend"""
        config = read_yaml_file("configs.yaml")
        try:
            return f"http://{config['flask_questionnaire']['ip']}:{config['flask_questionnaire']['port']}"
        except:
            return "http://localhost:5001"
    
    def get_questionnaire(self) -> Optional[Dict]:
        """Ottiene le domande del questionario dal backend"""
        try:
            response = requests.get(
                f"{self.base_url_questionnaire_flask}/get_questionnaire",
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
    
    def submit_answers(self, questions: Dict, answers: Dict) -> Dict:
        """Invia le risposte e lo schema del questionario al backend"""
        try:
            response = requests.post(
                f"{self.base_url_questionnaire_flask}/refine_questionnaire",
                json={
                    "questionnaire_schema": questions,
                    "user_answers": answers
                },
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                # Restituisce i dati della risposta
                return response.json()
            else:
                # In caso di errore, mostra l'errore e restituisce un dict con errore
                error_msg = response.json().get('error', 'Errore sconosciuto')
                st.error(f"Errore dal server: {error_msg}")
                return {"error": error_msg, "status_code": response.status_code}
                
        except requests.exceptions.Timeout:
            error_msg = "Timeout nella richiesta al server"
            st.error(error_msg)
            return {"error": error_msg}
        except requests.exceptions.ConnectionError:
            error_msg = "Errore di connessione al server"
            st.error(error_msg)
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"Errore nell'invio: {str(e)}"
            st.error(error_msg)
            return {"error": error_msg}

    def elaborate_worker_condition(self, questionnaire_schema: Dict, worker_answers: Dict, 
                                follow_up_questions: List, follow_up_answers: Dict) -> Dict:
        """Elabora la condizione del lavoratore dopo il completamento del questionario"""
        try:
            response = requests.post(
                f"{self.base_url_manager}/elaborate_worker_condition",
                json={
                    "questionnaire_schema": questionnaire_schema,
                    "worker_answers": worker_answers,
                    "follow_up_questions": follow_up_questions,
                    "follow_up_answers": follow_up_answers
                },
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                error_msg = response.json().get('error', 'Errore sconosciuto nell\'elaborazione')
                st.error(f"Errore nell'elaborazione: {error_msg}")
                return {"error": error_msg, "status_code": response.status_code}
                
        except requests.exceptions.Timeout:
            error_msg = "Timeout nell'elaborazione - il processo potrebbe richiedere più tempo"
            st.error(error_msg)
            return {"error": error_msg}
        except requests.exceptions.ConnectionError:
            error_msg = "Errore di connessione durante l'elaborazione"
            st.error(error_msg)
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"Errore nell'elaborazione: {str(e)}"
            st.error(error_msg)
            return {"error": error_msg}