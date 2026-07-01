import os
from google.cloud.sql.connector import Connector
import sqlalchemy
from ingest.chunker import parse_markdown_content
from ingest.embedder import get_embedding
from google.cloud import storage

BUCKET_NAME = "fictworks-rule-data-501004"
INSTANCE_CONNECTION_NAME = "my-project-rag-501004:asia-northeast1:rag-rules-db"
DB_USER = "rag_user"
DB_PASS = "RagUserPass456!"
DB_NAME = "rag_db"

def get_engine():
    connector = Connector()

    def getconn():
        return connector.connect(
            INSTANCE_CONNECTION_NAME,
            "pg8000",
            user=DB_USER,
            password=DB_PASS,
            db=DB_NAME,
        )

    engine = sqlalchemy.create_engine(
        "postgresql+pg8000://",
        creator=getconn,
    )
    return engine

def main():
    print("[INFO] データ取り込みバッチを開始します。")

    # GCSからファイル取得
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blobs = list(bucket.list_blobs(prefix="company_rule/"))

    all_chunks = []
    for blob in blobs:
        if not blob.name.endswith(".md"):
            continue
        if "00_概要_目次" in blob.name:
            continue

        filename = os.path.basename(blob.name)
        text = blob.download_as_text(encoding="utf-8")
        chunks = parse_markdown_content(filename, text)
        all_chunks.extend(chunks)
        print(f"[INFO] パース完了: {filename} ({len(chunks)} チャンク)")

    print(f"[INFO] 総チャンク数: {len(all_chunks)} 件 ベクトル化+DB格納を開始します。")

    engine = get_engine()
    with engine.connect() as conn:
        # 最初のTRUNCATEは即座に確定させる
        conn.execute(sqlalchemy.text("TRUNCATE TABLE rule_chunks;"))
        conn.commit() 

        success_count = 0
        for chunk in all_chunks:
            try:
                embedding = get_embedding(chunk["content"])
                conn.execute(
                    sqlalchemy.text("""
                        INSERT INTO rule_chunks
                            (source_file, chapter_title, article_no, article_title, content, embedding)
                        VALUES
                            (:source_file, :chapter_title, :article_no, :article_title, :content, :embedding)
                    """),
                    {
                        "source_file": chunk["source_file"],
                        "chapter_title": chunk["chapter_title"],
                        "article_no": chunk["article_no"],
                        "article_title": chunk["article_title"],
                        "content": chunk["content"],
                        "embedding": str(embedding),
                    }
                )
                # 【修正ポイント1】1件ごとにコミットしてデータを確定させる
                conn.commit()
                
                success_count += 1
                print(f"  [{success_count}] {chunk['source_file']} {chunk['article_no']} 登録完了")
                
            except Exception as e:
                # 【修正ポイント2】エラー時は即座にロールバックして、壊れたトランザクションをリセットする
                conn.rollback()
                print(f"[WARNING] スキップ: {chunk.get('article_no')} / エラー: {e}")

    # ループ外の conn.commit() は削除（または残しても無害ですが、各ループで確定させているため不要です）
    print(f"\n[SUCCESS] 完了！ 登録件数: {success_count} / {len(all_chunks)}")

if __name__ == "__main__":
    main()