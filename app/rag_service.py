import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from ingest.embedder import get_embedding
from app.db import search_similar_chunks
from app.llm_client import generate_answer

def answer_question(question: str) -> dict:
    if not question or not question.strip():
        raise ValueError("質問を入力してください。")
    if len(question) > 500:
        raise ValueError("質問は500文字以内で入力してください。")

    query_embedding = get_embedding(question)
    contexts = search_similar_chunks(query_embedding, top_k=3)
    contexts = [c for c in contexts if c["similarity"] >= 0.5]

    if not contexts:
        return {
            "answer": "就業規則内に関連する情報が見つかりませんでした。",
            "sources": []
        }

    # Geminiで回答生成
    answer = generate_answer(question, contexts)

    sources = [
        {
            "source_file": c["source_file"],
            "article_no": c["article_no"],
            "article_title": c["article_title"],
        }
        for c in contexts
    ]

    return {"answer": answer, "sources": sources}