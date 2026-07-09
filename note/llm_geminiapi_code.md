# Gemeni APIをPythonで使う関数（バックエンド）

## APIキーの設定
- 役割: Gemini API を使うための「認証（ログイン）」を行う関数です。
- なぜ重要か: これをプログラムの最初（モデルを呼び出す前）に実行しないと、Google のサーバーに拒否されてしまい、Gemini を一切動かすことができません。
```python
import google.generativeai as genai

# 鍵をセットして利用可能な状態にする
genai.configure(api_key="あなたのAPIキー")
```

## AIモデルの準備
- 役割: 使用したい Gemini のモデル（頭脳）を指定して、初期化するクラスです。
- なぜ重要か: Gemini には、かしこいモデルや、軽量で高速なモデルなど複数の種類があります。今回のプロジェクトで使用している最新の無料枠モデル gemini-2.5-flash-lite などを指定して、いつでも命令を送れる「AIのインスタンス」を作成します。
```python
# 使用する頭脳（モデル名）を指定して、model という変数に代入する
model = genai.GenerativeModel("gemini-2.5-flash-lite")
```

## 文章の生成
- 役割: 準備した AI モデルに指示文（プロンプト）を送り、回答（文章）を作ってもらう最重要関数です。
- なぜ重要か: チャットボットの回答を作成する心臓部です。返ってきた結果（オブジェクト）の .text という部分に、AIが考えてくれた回答の文字列が入っています。  
```python
# AIに指示を送る
response = model.generate_content("就業規則とは何ですか？簡潔に教えて。")

# 答えの文字だけを取り出して表示する
print(response.text)
```

## テキストのベクトル化
- 役割: テキスト（文章）を、コンピューターが計算しやすい「数字の羅列（ベクトル）」に変換する関数です。
- なぜ重要か: RAG システムを 0 から作る際、ユーザーの質問に近い就業規則をデータベース（pgvector）から検索するために絶対に不可欠な関数です。
```python
result = genai.embed_content(
    model="models/gemini-embedding-001",  # ベクトル化専用のモデルを指定
    content="有給休暇は何日ですか？",       # ベクトル化したい文章
    task_type="retrieval_document",        # 検索用であることを指定
    output_dimensionality=768              # 次元数を768に固定（超重要！）
)

# 数字のリスト（ベクトルデータ）を取り出す
query_vector = result["embedding"]
```
