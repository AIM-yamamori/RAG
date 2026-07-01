import os

# Gemini APIを利用するライブラリ
import google.generativeai as genai

# .envファイル読み込み用
from dotenv import load_dotenv



# .envの環境変数を読み込む
#
# 例:
# GEMINI_API_KEY=xxxxx
#
load_dotenv()



# Gemini APIキー設定
#
# APIを利用するための認証設定
genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)



# 文章をEmbedding(ベクトル)へ変換する関数
#
# 例:
#
# "年次有給休暇は10日付与される"
#
# ↓
#
# [
# 0.012,
# -0.034,
# ...
# ]
#
# 数値の配列へ変換する
#
def get_embedding(text: str) -> list[float]:



    # Gemini Embeddingモデルで変換
    result = genai.embed_content(

        # 使用するEmbeddingモデル
        model="models/gemini-embedding-001",


        # ベクトル化する文章
        content=text,


        # 検索用Embeddingとして作成
        #
        # RAGでは:
        # 文書保存 → retrieval_document
        # 質問検索 → retrieval_query
        #
        task_type="retrieval_document",


        # 出力するベクトルサイズ
        #
        # 今回は768次元
        output_dimensionality=768
    )



    # Geminiが返したベクトルだけ取得
    return result["embedding"]