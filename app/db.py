import os
import sqlalchemy
from google.cloud.sql.connector import Connector

INSTANCE_CONNECTION_NAME = "my-project-rag-501004:asia-northeast1:rag-rules-db"
DB_USER = "rag_user"
DB_PASS = "RagUserPass456!"
DB_NAME = "rag_db"

_engine = None

def get_engine():
    global _engine
    if _engine is None:
        connector = Connector()
        def getconn():
            return connector.connect(
                INSTANCE_CONNECTION_NAME,
                "pg8000",
                user=DB_USER,
                password=DB_PASS,
                db=DB_NAME,
            )
        _engine = sqlalchemy.create_engine(
            "postgresql+pg8000://",
            creator=getconn,
        )
    return _engine

def search_similar_chunks(query_embedding: list[float], top_k: int = 3) -> list[dict]:
    engine = get_engine()
    vector_str = "[" + ",".join(str(v) for v in query_embedding) + "]"
    sql = sqlalchemy.text("""
        SELECT source_file, chapter_title, article_no, article_title, content,
               1 - (embedding <=> CAST(:vec AS vector)) AS similarity
        FROM rule_chunks
        ORDER BY embedding <=> CAST(:vec AS vector)
        LIMIT :top_k
    """)
    results = []
    with engine.connect() as conn:
        rows = conn.execute(sql, {"vec": vector_str, "top_k": top_k})
        for r in rows:
            results.append({
                "source_file": r[0],
                "chapter_title": r[1],
                "article_no": r[2],
                "article_title": r[3],
                "content": r[4],
                "similarity": float(r[5]),
            })
    return results