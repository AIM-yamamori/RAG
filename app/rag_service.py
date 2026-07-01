import os
import sys


# 親ディレクトリをPythonの検索パスへ追加
# appからingestなど別フォルダを読み込むため
sys.path.append(
    os.path.join(os.path.dirname(__file__), "..")
)


# Embedding作成
# 質問文をベクトル化する
from ingest.embedder import get_embedding


# DBから似た文章を検索する
from app.db import search_similar_chunks


# Geminiで回答生成する
from app.llm_client import generate_answer



# =========================
# RAGメイン処理
# =========================
#
# 流れ:
#
# 質問
# ↓
# embedding作成
# ↓
# 類似文章検索
# ↓
# Gemini回答生成
#
def answer_question(question: str) -> dict:


    # 入力チェック
    if not question or not question.strip():

        raise ValueError(
            "質問を入力してください。"
        )


    # 長すぎる質問を防止
    if len(question) > 500:

        raise ValueError(
            "質問は500文字以内で入力してください。"
        )



    # 質問をベクトル化
    #
    # 例:
    # "有給休暇は何日?"
    #
    # ↓
    # [0.12, -0.03, ...]
    #
    query_embedding = get_embedding(
        question
    )



    # ベクトル検索
    #
    # 質問に近い条文を取得
    # 上位3件取得
    contexts = search_similar_chunks(
        query_embedding,
        top_k=3
    )



    # 類似度が低い結果を除外
    #
    # 0.5未満は関連性が低いと判断
    contexts = [
        c
        for c in contexts
        if c["similarity"] >= 0.5
    ]



    # 関連する条文がない場合
    if not contexts:

        return {
            "answer":
                "就業規則内に関連する情報が見つかりませんでした。",

            "sources": []
        }



    # 検索した条文を使って
    # Geminiに回答生成させる
    answer = generate_answer(
        question,
        contexts
    )



    # 画面表示用に参照元情報を作成
    sources = [

        {
            "source_file": c["source_file"],
            "article_no": c["article_no"],
            "article_title": c["article_title"],
        }

        for c in contexts
    ]



    # 回答と参照元を返す
    return {
        "answer": answer,
        "sources": sources
    }