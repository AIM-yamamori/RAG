import os
import time
import google.generativeai as genai
from dotenv import load_dotenv


# .envファイルから環境変数を読み込む
load_dotenv()


# Geminiで回答を生成する関数
# question: ユーザーの質問
# contexts: RAG検索で取得した関連文章
def generate_answer(question: str, contexts: list[dict]) -> str:


    # Gemini APIキー取得
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "環境変数 GEMINI_API_KEY が設定されていません"
        )


    # Gemini API設定
    genai.configure(api_key=api_key)


    # 使用するGeminiモデル
    model = genai.GenerativeModel(
        "gemini-2.5-flash-lite"
    )


    # 検索結果(条文)をGeminiへ渡す文章に変換
    context_block = ""

    for c in contexts:

        context_block += (
            f"[出典: {c['source_file']} "
            f"{c['article_no']}({c['article_title']})]\n"
            f"{c['content']}\n\n"
        )


    # Geminiへの指示文
    prompt = f"""
あなたは株式会社フィクトワークスの就業規則について回答する社内アシスタントです。

以下の参考情報だけを使って回答してください。
情報がない場合は推測せず、
「就業規則内に該当する情報が見つかりませんでした」
と回答してください。

【参考情報】
{context_block}

【質問】
{question}

【回答】
"""


    # APIエラー時は1回リトライ
    for attempt in range(1, 3):

        try:

            # Geminiへ送信
            response = model.generate_content(prompt)

            # 回答本文を返す
            return response.text


        except Exception as e:

            # 2回失敗したらエラー
            if attempt == 2:
                raise RuntimeError(
                    f"Gemini API呼び出し失敗: {e}"
                )

            # 少し待って再実行
            time.sleep(3)