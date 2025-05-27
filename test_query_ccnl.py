import os
from know_your_worth.rag.rag_engine import RAGEngine

rag = RAGEngine(
    db_dir="./index/ccnl",
    collection_name="ccnl",
    llm_api_key=os.getenv("SONAR_API_KEY"),
    llm_model=os.getenv("SONAR_API_MODEL"),
    openai_api_key=os.getenv("OPENAI_API_KEY"),
)

# Esegui la query
query_refinement_by_llm = """
- Superamento del limite orario giornaliero e settimanale previsto dal CCNL agricolo per lavoro stagionale
- Retribuzione globale mensile inferiore ai minimi tabellari previsti dal CCNL per operai agricoli
- Assenza di contratto individuale scritto come richiesto dalla normativa e dal CCNL di settore
- Pagamento in contanti in violazione dell’obbligo di tracciabilità retributiva
- Mancato riconoscimento e pagamento delle ore di lavoro straordinario festivo e domenicale
- Negazione del diritto alle ferie retribuite e ai riposi settimanali obbligatori
- Inadeguata tutela contro gli infortuni e mancanza di copertura assicurativa obbligatoria INAIL
- Condotte di pressione e intimidazione lesive dei diritti sindacali e della libertà di denuncia
"""

query = f"""
Queste sono le condizioni riassuntive del lavoratore:
{query_refinement_by_llm}

Spiega in base ai documenti ottenuti, se e perché il lavoratore è sfruttato"""
response = rag.query(query)

print("\n🧠 Risposta RAG:")
print(response)
