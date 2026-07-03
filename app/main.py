import streamlit as st
import os
import sys

# 親ディレクトリをPythonの検索パスへ追加（既存の記述を移植）
sys.path.append(
    os.path.join(os.path.dirname(__file__), "..")
)

# RAGのコアロジックをインポート
from app.rag_service import answer_question

# ページの設定
st.set_page_config(
    page_title="就業規則RAGチャットボット",
    page_icon="💼",
    layout="centered"
)

st.title("💼 就業規則チャットボット")
st.caption("株式会社フィクトワークス | 就業規則について質問を入力してください")

# 会話履歴（セッション状態）の初期化
if "messages" not in st.session_state:
    st.session_state.messages = []

# 画面リロード時に、過去の会話履歴を再描画
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        # アシスタントのメッセージで、かつ出典情報がある場合は st.expander で表示
        if msg["role"] == "assistant" and msg.get("sources"):
            with st.expander("📄 出典"):
                for s in msg["sources"]:
                    st.write(f"- {s['source_file']} {s['article_no']}({s['article_title']})")

# ユーザーからの質問入力受付（Enterで送信）
if question := st.chat_input("就業規則について質問してください..."):
    
    # 1. ユーザーの質問を画面に表示 & 履歴に追加
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    # 2. アシスタントの回答領域を作成
    with st.chat_message("assistant"):
        # 回答生成中のローディング表示（スピナー）
        with st.spinner("回答を生成中..."):
            try:
                # 既存のRAGメイン処理をそのまま呼び出し
                result = answer_question(question)
                answer = result["answer"]
                sources = result["sources"]
                
            except ValueError as e:
                # 文字数オーバーなどのバリデーションエラー時の処理
                answer = f"入力エラー: {str(e)}"
                sources = []
            except Exception as e:
                # その他のシステムエラー時の処理
                answer = "回答の生成中にエラーが発生しました。しばらくしてから再度お試しください。"
                sources = []

        # 回答本文を表示
        st.write(answer)
        
        # 出典情報（sources）がある場合は折りたたみ表示
        if sources:
            with st.expander("📄 出典"):
                for s in sources:
                    st.write(f"- {s['source_file']} {s['article_no']}({s['article_title']})")

    # 3. アシスタントの回答と出典を履歴に追加
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources
    })