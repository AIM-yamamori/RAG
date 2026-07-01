import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from ingest.embedder import get_embedding
from app.db import search_similar_chunks

def answer_question(question: str) -> dict:
    if not question or not question.strip():
        raise ValueError("質問を入力してください。")

    print(f"[DEBUG] 質問: {question}")

    # ベクトル化
    try:
        query_embedding = get_embedding(question)
        print(f"[DEBUG] embedding取得成功: 次元数={len(query_embedding)}")
    except Exception as e:
        print(f"[DEBUG] embedding失敗: {e}")
        raise

    # 検索
    try:
        contexts = search_similar_chunks(query_embedding, top_k=3)
        print(f"[DEBUG] 検索結果件数: {len(contexts)}")
        print(f"[DEBUG] 検索結果内容: {contexts}")
    except Exception as e:
        print(f"[DEBUG] 検索失敗: {e}")
        raise

    if not contexts:
        return {
            "answer": "就業規則内に関連する情報が見つかりませんでした。",
            "sources": []
        }

    answer_parts = []
    for c in contexts:
        print(f"[DEBUG] チャンク: {c}")
        answer_parts.append(
            f"【{c['article_no']}({c['article_title']}) 類似度:{c['similarity']:.3f}】\n{c['content']}"
        )
    answer = "\n\n---\n\n".join(answer_parts)

    sources = [
        {
            "source_file": c["source_file"],
            "article_no": c["article_no"],
            "article_title": c["article_title"],
        }
        for c in contexts
    ]

    return {"answer": answer, "sources": sources}