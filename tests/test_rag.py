# test_rag.py
import os
from dotenv import load_dotenv

# .env を読み込み
load_dotenv()

# 読み込みの確認
print("=== 環境変数チェック ===")
print(f"GOOGLE_CLOUD_PROJECT: {os.getenv('GOOGLE_CLOUD_PROJECT')}")
print(f"GEMINI_API_KEY: {'設定あり' if os.getenv('GEMINI_API_KEY') else '設定なし'}")
print("========================\n")

from app.rag_service import answer_question

def run_test(question: str):
    print(f"◆ 質問: {question}")
    print("-" * 50)
    try:
        # RAGコアロジックを呼び出し
        result = answer_question(question)
        
        print("🤖 AIの回答:")
        print(result["answer"])
        print("\n📄 出典情報:")
        for idx, source in enumerate(result["sources"], 1):
            print(f"  [{idx}] {source['source_file']} {source.get('article_no', '')} {source.get('article_title', '')}")
            
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
    print("=" * 50 + "\n")

if __name__ == "__main__":
    # テストパターン1: 就業規則にあるはずの質問
    run_test("試用期間は何ヶ月ですか？")
    
    # テストパターン2: 就業規則にないはずの質問
    run_test("会社の創立記念日はいつですか？")