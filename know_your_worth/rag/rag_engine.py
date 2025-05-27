from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.ingestion import IngestionPipeline
import chromadb
from pathlib import Path

from .perplexity_llm import PerplexityLLM  # Assuming this is the correct import path for your custom LLM


class RAGEngine:
    def __init__(self, 
                 db_dir: str, 
                 collection_name: str, 
                 llm_api_key: str, 
                 llm_model: str = "sonar-pro", 
                 embedding_model: str = "text-embedding-3-small",
                 openai_api_key: str = None):
        self.db_dir = Path(db_dir)
        self.collection_name = collection_name
        
        # Setup global Settings
        Settings.llm = PerplexityLLM(model_name=llm_model, api_key=llm_api_key, )  # OpenAI(model=llm_model, api_key=llm_api_key, base_url="https://api.perplexity.ai")
        Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small", api_key=openai_api_key)  # HuggingFaceEmbedding(model_name=embedding_model)

        self.chroma_client = chromadb.PersistentClient(path=str(self.db_dir))
        self.chroma_collection = self.chroma_client.get_or_create_collection(name=self.collection_name)
        self.vector_store = ChromaVectorStore(chroma_collection=self.chroma_collection)

        self.index = VectorStoreIndex.from_vector_store(self.vector_store)

    def ingest_documents(self, docs):
        pipeline = IngestionPipeline(
            transformations=[
                SentenceSplitter(chunk_size=1200, chunk_overlap=150),
                Settings.embed_model
            ],
            vector_store=self.vector_store
        )
        pipeline.run(documents=docs)

    def query(self, prompt: str, top_k: int = 3):
        # retriever = self.index.as_retriever(similarity_top_k=top_k)
        query_engine = self.index.as_query_engine()
        response = query_engine.query(prompt)
        return response  # retriever.retrieve(prompt)
