import logging
import os
import sys

import streamlit as st

# 親ディレクトリをPython検索パスへ追加
sys.path.append(
    os.path.join(os.path.dirname(__file__), "..")
)

from app.rag_service import answer_question

# -----------------------------
# ログ設定
# -----------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 開発環境用フラグ
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# 最大入力文字数
MAX_QUESTION_LENGTH = 200

# -----------------------------
# ページ設定
# -----------------------------
st.set_page_config(
    page_title="就業規則RAGチャットボット",
    page_icon="💼",
    layout="centered"
)

st.title("💼 就業規則チャットボット")
st.caption("株式会社フィクトワークス | 就業規則について質問を入力してください")

# -----------------------------
# セッション初期化
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------
# 出典表示
# -----------------------------
def show_sources(sources):
    """
    出典一覧を表示する
    """
    if not sources:
        return

    with st.expander("📄 出典"):
        for s in sources:
            source_file = s.get("source_file", "不明")
            article_no = s.get("article_no", "")
            article_title = s.get("article_title", "")

            st.write(
                f"- {source_file} {article_no} ({article_title})"
            )

# -----------------------------
# 会話履歴表示
# -----------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

        if msg["role"] == "assistant":
            show_sources(msg.get("sources", []))

# -----------------------------
# 入力受付
# -----------------------------
if question := st.chat_input("就業規則について質問してください..."):

    # 前後の空白削除
    question = question.strip()

    # 空文字チェック
    if not question:
        st.warning("質問を入力してください。")
        st.stop()

    # 文字数チェック
    if len(question) > MAX_QUESTION_LENGTH:
        st.warning(
            f"質問は{MAX_QUESTION_LENGTH}文字以内で入力してください。"
        )
        st.stop()

    # ユーザー発言表示
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.write(question)

    # 初期値
    answer = ""
    sources = []

    # -----------------------------
    # 回答生成
    # -----------------------------
    with st.chat_message("assistant"):

        with st.spinner("回答を生成中..."):

            try:
                logger.info("質問受付: %s", question)

                result = answer_question(question)

                if result is None:
                    raise RuntimeError(
                        "answer_question() が None を返しました。"
                    )

                answer = result.get(
                    "answer",
                    "回答を取得できませんでした。"
                )

                sources = result.get(
                    "sources",
                    []
                )

            except ValueError as e:

                logger.warning("入力エラー: %s", e)

                answer = f"入力エラー: {e}"

            except TimeoutError as e:

                logger.exception("タイムアウト")

                answer = (
                    "処理がタイムアウトしました。"
                    "時間をおいて再度お試しください。"
                )

            except ConnectionError as e:

                logger.exception("接続エラー")

                answer = (
                    "サーバーへ接続できませんでした。"
                    "しばらくしてから再度お試しください。"
                )

            except Exception as e:

                logger.exception("回答生成中に予期しないエラー")

                if DEBUG:
                    st.exception(e)

                answer = (
                    "回答の生成中にエラーが発生しました。"
                    "しばらくしてから再度お試しください。"
                )

        # 回答表示
        st.write(answer)

        # 出典表示
        show_sources(sources)

    # -----------------------------
    # 会話履歴保存
    # -----------------------------
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources
    })