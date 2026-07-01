import os

# SQL操作用
import sqlalchemy

# Cloud SQL接続用
from google.cloud.sql.connector import Connector



# Cloud SQL接続情報
INSTANCE_CONNECTION_NAME = (
    "my-project-rag-501004:asia-northeast1:rag-rules-db"
)

DB_USER = "rag_user"
DB_PASS = "RagUserPass456!"
DB_NAME = "rag_db"



# DB接続を使い回すための変数
_engine = None



# =========================
# DB接続作成
# =========================

def get_engine():

    global _engine


    # 初回だけ接続作成
    #
    # 何度もDB接続を作らないため
    if _engine is None:


        # Cloud SQL Connector作成
        connector = Connector()



        # DB接続処理
        def getconn():

            return connector.connect(

                INSTANCE_CONNECTION_NAME,

                "pg8000",

                user=DB_USER,
                password=DB_PASS,
                db=DB_NAME,
            )



        # SQLAlchemyエンジン作成
        _engine = sqlalchemy.create_engine(

            "postgresql+pg8000://",

            creator=getconn,
        )


    return _engine




# =========================
# 類似チャンク検索
# =========================
#
# 質問ベクトル
# ↓
# pgvector検索
# ↓
# 近い条文取得
#
def search_similar_chunks(
    query_embedding: list[float],
    top_k: int = 3
) -> list[dict]:



    # DB接続取得
    engine = get_engine()



    # Python配列をpgvector形式へ変換
    #
    # [0.1,0.2,0.3]
    #
    # ↓
    #
    # "[0.1,0.2,0.3]"
    #
    vector_str = (
        "["
        + ",".join(
            str(v)
            for v in query_embedding
        )
        + "]"
    )



    # 類似度検索SQL
    #
    # embedding <=> vector
    #
    # ↓
    #
    # ベクトル距離を計算
    #
    # 距離が小さいほど似ている
    #
    sql = sqlalchemy.text(
        """
        SELECT
            source_file,
            chapter_title,
            article_no,
            article_title,
            content,

            1 - (
                embedding <=> CAST(:vec AS vector)
            )
            AS similarity

        FROM rule_chunks

        ORDER BY
            embedding <=> CAST(:vec AS vector)

        LIMIT :top_k
        """
    )



    results = []



    # SQL実行
    with engine.connect() as conn:


        rows = conn.execute(

            sql,

            {
                "vec": vector_str,
                "top_k": top_k
            }

        )



        # DB結果を辞書形式へ変換
        for r in rows:


            results.append(

                {

                    # ファイル名
                    "source_file": r[0],


                    # 章タイトル
                    "chapter_title": r[1],


                    # 条文番号
                    "article_no": r[2],


                    # 条文タイトル
                    "article_title": r[3],


                    # 条文本文
                    "content": r[4],


                    # 類似度
                    "similarity": float(r[5]),
                }

            )


    return results