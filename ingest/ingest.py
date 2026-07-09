import os
import time  # ➕ 【追加】時間制御用のライブラリをインポート
# Cloud SQL接続用
from google.cloud.sql.connector import Connector
# DB操作用
import sqlalchemy
# Markdownを条文単位へ分割
from ingest.chunker import parse_markdown_content
# 文章をベクトル化
from ingest.embedder import get_embedding
# GCS操作用
from google.cloud import storage

from dotenv import load_dotenv
load_dotenv()

# GCS保存先
BUCKET_NAME = os.getenv("BUCKET_NAME")

# Cloud SQL接続情報
INSTANCE_CONNECTION_NAME = os.getenv("INSTANCE_CONNECTION_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")


# =========================
# DB接続作成
# =========================
def get_engine():
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

    # SQLAlchemyの接続設定
    engine = sqlalchemy.create_engine(
        "postgresql+pg8000://",
        creator=getconn,
    )
    return engine


# =========================
# データ取り込み処理
# =========================
def main():
    print(
        "[INFO] データ取り込みバッチを開始します。"
    )

    # =========================
    # GCSからMarkdown取得
    # =========================
    client = storage.Client()
    bucket = client.bucket(
        BUCKET_NAME
    )

    # company_ruleフォルダ内取得
    blobs = list(
        bucket.list_blobs(
            prefix="company_rule/"
        )
    )

    all_chunks = []

    # ファイルごとに処理
    for blob in blobs:
        # Markdown以外は除外
        if not blob.name.endswith(".md"):
            continue

        # 目次ファイルは除外
        if "00_概要_目次" in blob.name:
            continue

        # ファイル名取得
        filename = os.path.basename(
            blob.name
        )

        # GCSから本文取得
        text = blob.download_as_text(
            encoding="utf-8"
        )

        # 条文単位へ分割
        chunks = parse_markdown_content(
            filename,
            text
        )

        # 全チャンクへ追加
        all_chunks.extend(
            chunks
        )

        print(
            f"[INFO] パース完了: {filename} ({len(chunks)} チャンク)"
        )

    print(
        f"[INFO] 総チャンク数: {len(all_chunks)} 件 "
        "ベクトル化+DB格納を開始します。"
    )

    # =========================
    # DBへ保存
    # =========================
    engine = get_engine()

    with engine.connect() as conn:
        # 既存データ削除（再取り込み時に古いデータを消す）
        conn.execute(
            sqlalchemy.text(
                "TRUNCATE TABLE rule_chunks;"
            )
        )
        conn.commit()

        success_count = 0

        # チャンクごとに登録
        for chunk in all_chunks:
            try:
                # ❌ 【問題の箇所】本文をEmbedding化（ここでAPIを大量消費していた）
                embedding = get_embedding(
                    chunk["content"],
                    task_type="retrieval_document"
                )

                # DBへ登録
                conn.execute(
                    sqlalchemy.text(
                        """
                        INSERT INTO rule_chunks
                            (
                             source_file,
                             chapter_title,
                             article_no,
                             article_title,
                             content,
                             embedding
                            )
                        VALUES
                            (
                             :source_file,
                             :chapter_title,
                             :article_no,
                             :article_title,
                             :content,
                             :embedding
                            )
                        """
                    ),
                    {
                        "source_file": chunk["source_file"],
                        "chapter_title": chunk["chapter_title"],
                        "article_no": chunk["article_no"],
                        "article_title": chunk["article_title"],
                        "content": chunk["content"],
                        "embedding": str(embedding), # DB保存用に文字列化
                    }
                )

                # 1件ごとに確定
                conn.commit()
                success_count += 1

                print(
                    f"[{success_count}] "
                    f"{chunk['source_file']} "
                    f"{chunk['article_no']} 登録完了"
                )

                # ⭕ 【修正】Google APIに怒られないよう、1回登録するごとに1秒休憩を入れる
                # これにより、1分間の最大リクエスト数が「60回」に確実に制限され、RPM制限（上限100回）を100%回避できます。
                time.sleep(1)

            except Exception as e:
                # エラー時は取り消し
                conn.rollback()
                print(
                    f"[WARNING] スキップ: "
                    f"{chunk.get('article_no')} / エラー: {e}"
                )

    print(
        f"\n[SUCCESS] 完了！ "
        f"登録件数: {success_count} / {len(all_chunks)}"
    )


# このファイルを直接実行した時だけ実行
if __name__ == "__main__":
    main()