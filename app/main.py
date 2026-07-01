# FastAPIでAPIを作成するための機能
# HTTPExceptionはエラー返却に使用
from fastapi import FastAPI, HTTPException

# HTMLを返すために使用
from fastapi.responses import HTMLResponse

# JSONデータの型チェックに使用
from pydantic import BaseModel, Field

# ファイルパス操作に使用
import os


# RAG処理を呼び出す関数
# 質問
# ↓
# ベクトル検索
# ↓
# Gemini回答生成
from app.rag_service import answer_question



# FastAPIアプリ作成
app = FastAPI(title="就業規則RAGチャットボット")



# =========================
# 受信データ形式
# =========================

# ユーザーから送られる質問データ
#
# 例:
# {
#   "question": "有給休暇は何日ですか"
# }
class ChatRequest(BaseModel):

    # 質問文
    # 必須、1〜500文字
    question: str = Field(
        ...,
        min_length=1,
        max_length=500
    )



# =========================
# 返却データ形式
# =========================


# 検索元情報
class SourceInfo(BaseModel):

    # 参照したファイル名
    source_file: str

    # 条文番号
    article_no: str | None = None

    # 条文タイトル
    article_title: str | None = None



# APIレスポンス形式
class ChatResponse(BaseModel):

    # Geminiが生成した回答
    answer: str

    # 回答に使用した資料情報
    sources: list[SourceInfo]



# =========================
# 動作確認用API
# =========================

@app.get("/api/health")
def health():

    # サーバー起動確認用
    return {"status": "ok"}



# =========================
# チャットAPI
# =========================

@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    try:

        # 質問をRAG処理へ渡す
        result = answer_question(
            request.question
        )


        # 返却形式へ変換
        return ChatResponse(

            # 回答本文
            answer=result["answer"],


            # 検索結果をSourceInfo形式へ変換
            sources=[
                SourceInfo(**s)
                for s in result["sources"]
            ]
        )


    # 入力エラー
    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


    # その他エラー
    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )



# =========================
# HTML表示
# =========================

@app.get("/", response_class=HTMLResponse)
def index():


    # index.htmlの場所を取得
    #
    # app/
    #  └ static/
    #       └ index.html
    #
    html_path = os.path.join(
        os.path.dirname(__file__),
        "static",
        "index.html"
    )


    # HTMLを読み込んで返す
    with open(
        html_path,
        encoding="utf-8"
    ) as f:

        return f.read()