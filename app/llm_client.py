import os
import time
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()  # .envファイルを読み込む

def generate_answer(question: str, contexts: list[dict]) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("環境変数 GEMINI_API_KEY が設定されていません")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    context_block = ""
    for c in contexts:
        context_block += (
            f"[出典: {c['source_file']} {c['article_no']}({c['article_title']})]\n"
            f"{c['content']}\n\n"
        )

    prompt = f"""あなたは株式会社フィクトワークスの就業規則について回答する社内アシスタントです。
以下の「参考情報」のみを根拠として、質問に対して日本語で簡潔かつ正確に回答してください。
参考情報に記載がない内容については、推測で答えず「就業規則内に該当する情報が見つかりませんでした」と回答してください。

【参考情報】
{context_block}
【質問】
{question}

【回答】"""

    for attempt in range(1, 3):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            if attempt == 2:
                raise RuntimeError(f"Gemini API呼び出し失敗: {e}")
            time.sleep(3)