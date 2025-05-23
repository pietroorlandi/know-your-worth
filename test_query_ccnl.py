import os
from know_your_worth.rag.rag_engine import RAGEngine

rag = RAGEngine(
    db_dir="./index/ccnl",
    collection_name="ccnl",
    llm_api_key=os.getenv("SONAR_API_KEY"),
    llm_model=os.getenv("SONAR_API_MODEL"),
)

# Esegui la query
query = "A chi si applica il CCNL per impiegati agricoli?"
response = rag.query(query)

print("\n🧠 Risposta RAG:")
print(response)
