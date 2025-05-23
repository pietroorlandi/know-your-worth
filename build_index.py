import argparse
import os
from know_your_worth.rag.rag_engine import RAGEngine
from llama_index.core import SimpleDirectoryReader


parser = argparse.ArgumentParser()
parser.add_argument("--target", choices=["ccnl", "solutions"], required=True)
args = parser.parse_args()

if args.target == "ccnl":
    rag = RAGEngine(
        db_dir="./index/ccnl",
        collection_name="ccnl",
        llm_api_key=os.getenv("SONAR_API_KEY"),
        llm_model=os.getenv("SONAR_API_MODEL")
    )
    docs = SimpleDirectoryReader("data/ccnl").load_data()
    rag.ingest_documents(docs)
    print("✅ Indice CCNL creato.")
elif args.target == "solutions":
    pass
#     rag = RAGEngine(data_path="data/solutions", persist_dir="index/solutions")

# rag.load_and_index()
# print(f"{args.target} index created.")
