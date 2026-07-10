import os
import time
import logging

from dotenv import load_dotenv

# Cloud SQL接続
from google.cloud.sql.connector import Connector

# SQLAlchemy
import sqlalchemy

# GCS
from google.cloud import storage

# 条文分割
from ingest.chunker import parse_markdown_content

# Embedding生成
from ingest.embedder import get_embedding


# =========================
# ログ設定
# =========================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

logger = logging.getLogger(__name__)


# =========================
# .env読み込み
# =========================
load_dotenv()

BUCKET_NAME = os.getenv("BUCKET_NAME")

INSTANCE_CONNECTION_NAME = os.getenv("INSTANCE_CONNECTION_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")


# =========================
# Cloud SQL接続
# =========================
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

    return sqlalchemy.create_engine(
        "postgresql+pg8000://",
        creator=getconn,
    )


# =========================
# メイン処理
# =========================
def main():

    logger.info("データ取り込み開始")

    # -------------------------
    # GCS接続
    # -------------------------
    try:

        client = storage.Client()

        bucket = client.bucket(
            BUCKET_NAME
        )

        blobs = list(
            bucket.list_blobs(
                prefix="company_rule/"
            )
        )

        logger.info(
            "Markdownファイル取得: %d件",
            len(blobs)
        )

    except Exception:

        logger.exception(
            "GCS接続に失敗しました。"
        )
        return

    all_chunks = []

    # -------------------------
    # Markdown読み込み
    # -------------------------
    for blob in blobs:

        if not blob.name.endswith(".md"):
            continue

        if "00_概要_目次" in blob.name:
            continue

        try:

            filename = os.path.basename(
                blob.name
            )

            text = blob.download_as_text(
                encoding="utf-8"
            )

            chunks = parse_markdown_content(
                filename,
                text
            )

            all_chunks.extend(
                chunks
            )

            logger.info(
                "%s : %dチャンク",
                filename,
                len(chunks)
            )

        except Exception:

            logger.exception(
                "%s の読み込み失敗",
                blob.name
            )

    logger.info(
        "総チャンク数: %d",
        len(all_chunks)
    )

    # -------------------------
    # Cloud SQL接続
    # -------------------------
    try:

        engine = get_engine()

    except Exception:

        logger.exception(
            "Cloud SQL接続失敗"
        )
        return

    # -------------------------
    # DB保存
    # -------------------------
    with engine.connect() as conn:

        try:

            conn.execute(
                sqlalchemy.text(
                    "TRUNCATE TABLE rule_chunks;"
                )
            )

            conn.commit()

            logger.info(
                "既存データ削除完了"
            )

        except Exception:

            logger.exception(
                "テーブル初期化失敗"
            )

            return

        success_count = 0

        for chunk in all_chunks:

            try:

                # Embedding生成
                embedding = get_embedding(
                    chunk["content"],
                    task_type="retrieval_document"
                )

                # DB登録
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
                        "embedding": str(
                            embedding
                        ),
                    }
                )

                conn.commit()

                success_count += 1

                logger.info(
                    "[%d] %s 登録完了",
                    success_count,
                    chunk["article_no"]
                )

                # API制限対策
                time.sleep(1)

            except Exception as e:

                conn.rollback()

                logger.warning(
                    "%s 登録失敗: %s",
                    chunk.get(
                        "article_no",
                        "Unknown"
                    ),
                    e
                )

                continue

    logger.info(
        "データ取り込み完了 (%d/%d件)",
        success_count,
        len(all_chunks)
    )


# =========================
# エントリーポイント
# =========================
if __name__ == "__main__":

    try:

        main()

    except Exception:

        logger.exception(
            "予期しないエラーが発生しました。"
        )