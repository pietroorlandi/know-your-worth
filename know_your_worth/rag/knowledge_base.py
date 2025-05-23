from know_your_worth.rag.rag_engine import RAGEngine


class KnowledgeBase:
    def __init__(self, path_ccnl: str, path_solutions: str, api_key: str):
        self.ccnl_rag = RAGEngine(data_path=path_ccnl, api_key=api_key)
        self.solutions_rag = RAGEngine(data_path=path_solutions, api_key=api_key)

    def query_ccnl(self, q: str):
        return self.ccnl_rag.query(q)

    def query_solutions(self, q: str):
        return self.solutions_rag.query(q)
