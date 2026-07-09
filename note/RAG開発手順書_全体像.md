# 就業規則RAGチャットボット 開発手順書

## 文書情報

| 項目 | 内容 |
|---|---|
| プロジェクト名 | 就業規則RAGチャットボット(学習用) |
| 対象読者 | Python初心者〜中級者、Google Cloud初学者 |
| 作成日 | 2026年7月2日 |
| 想定期間 | 3〜4日間 |
| 前提知識 | Pythonの基本文法、コマンドライン操作の基礎 |

---

## このドキュメントの目的

Google Cloud上でRAG(Retrieval-Augmented Generation)システムを0から構築するための、完全な手順書である。設計・環境構築・実装・デプロイまでの全工程を網羅する。

---

## システム完成イメージ

```
ユーザーがブラウザで以下のURLにアクセス
https://rag-rules-chatbot-xxxx.run.app

↓

Streamlitのチャット画面が表示される

↓

「年次有給休暇は何日もらえますか？」と入力

↓

システムが就業規則82条文から関連条文を検索し
Geminiが自然文で回答を生成

↓

「勤続6か月で10日、6年6か月以上で最大20日の
年次有給休暇が付与されます。(出典: 第28条)」
```

---

## 技術スタック

| 役割 | 採用技術 | 理由 |
|---|---|---|
| 言語 | Python 3.12 | 全工程をPythonで統一 |
| フロントエンド | Streamlit | Pythonのみ。JS不要。チャットUI標準搭載 |
| ベクトルDB | Cloud SQL + pgvector | 低コスト。停止/削除でコスト管理しやすい |
| Embedding | Gemini API(gemini-embedding-001, 768次元) | 無料枠あり。安定動作確認済み |
| LLM | Gemini API(gemini-2.5-flash-lite) | 無料枠あり。安定動作確認済み |
| ホスティング | Cloud Run | リクエストがない時間は課金ゼロ |
| ファイル格納 | Google Cloud Storage | Markdownファイルの格納場所 |
| 秘匿情報管理 | 環境変数(.env / Cloud Run環境変数) | シンプルで学習に適している |

---

## フェーズ全体像

```
フェーズ1: 設計(1日目)
  ↓
フェーズ2: GCP環境構築(1日目)
  ↓
フェーズ3: ローカル開発環境構築(1日目)
  ↓
フェーズ4: Cloud SQL構築(1日目)
  ↓
フェーズ5: データ取り込みパイプライン実装(2日目)
  ↓
フェーズ6: バックエンド実装(2日目)
  ↓
フェーズ7: Streamlit UI実装・ローカル動作確認(2〜3日目)
  ↓
フェーズ8: Cloud Runデプロイ(3日目)
  ↓
完成: ブラウザから公開URLでRAGを利用できる状態
```

---

## フェーズ1: 設計

### 目的

何を作るかを明確にする。実装前に全体像を把握することで、手戻りを防ぐ。

### 成果物

- 要件定義書
- 概要設計書
- 基本設計書
- 詳細設計書

### 作業内容

**1-1. システム構成を決める**

以下の問いに答える形で構成を決定する。

| 問い | 今回の答え |
|---|---|
| 知識源は何か | 就業規則Markdown 11ファイル、82条文 |
| ベクトルDBは何を使うか | Cloud SQL + pgvector |
| Embeddingは何を使うか | Gemini API(gemini-embedding-001) |
| LLMは何を使うか | Gemini API(gemini-2.5-flash-lite) |
| UIは何で作るか | Streamlit(Python) |
| どこで動かすか | Cloud Run |

**1-2. ディレクトリ構成を決める**

```
rag-rules-chatbot/
├── requirements.txt
├── .env
├── .env.example
├── Dockerfile
├── data/
│   └── fictworks_rules/      # 就業規則.md × 11ファイル
├── ingest/
│   ├── chunker.py            # Markdown → 条文単位に分割
│   ├── embedder.py           # テキスト → ベクトル変換
│   └── ingest.py             # 取り込みバッチ本体
├── app/
│   ├── main.py               # Streamlitアプリ
│   ├── rag_service.py        # RAGコアロジック
│   ├── db.py                 # Cloud SQL接続・検索
│   └── llm_client.py         # Gemini API(回答生成)
└── tests/
    ├── test_embedding.py     # Embedding単体テスト
    ├── test_search.py        # 検索単体テスト
    └── test_rag.py           # RAG統合テスト
```

**1-3. データフローを整理する**

```
[就業規則.md × 11ファイル]
      ↓ chunker.py: ##第n条 単位で分割
[チャンク × 82件]
      ↓ embedder.py: Gemini Embedding API
[768次元ベクトル × 82件]
      ↓ ingest.py: Cloud SQLへINSERT
[rule_chunksテーブル(本文 + メタデータ + ベクトル)]

--- 取り込みここまで(1回のみ実行) ---

[ユーザーの質問文]
      ↓ embedder.py: Gemini Embedding API
[768次元クエリベクトル]
      ↓ db.py: pgvectorコサイン類似度検索
[関連条文 上位3件]
      ↓ llm_client.py: Geminiへプロンプト送信
[自然文の回答 + 出典情報]
      ↓ Streamlit画面に表示
```

### 完了確認

- [ ] 何を作るかが明確になっている
- [ ] ディレクトリ構成が決まっている
- [ ] データフローが理解できている

---

## フェーズ2: GCP環境構築

### 目的

Google Cloud上に作業環境を用意する。課金管理を最初に設定することが最重要。

### 前提条件

- Googleアカウントを持っている
- クレジットカードを登録済みである(無料クレジット$300付与)

### 作業内容

**2-1. GCPプロジェクトの作成**

1. https://console.cloud.google.com にアクセス
2. 「プロジェクトを作成」をクリック
3. プロジェクト名を入力(例: `rag-rules-chatbot`)
4. 作成されたプロジェクトIDをメモする(例: `my-project-rag-501004`)

**2-2. 予算アラートの設定(最優先)**

想定外の課金を防ぐため、必ずプロジェクト作成直後に設定する。

1. https://console.cloud.google.com/billing にアクセス
2. 「予算とアラート」→「予算を作成」
3. 以下のように設定する

| 項目 | 設定値 |
|---|---|
| 対象プロジェクト | 作成したプロジェクト |
| 予算額 | 2,000円 |
| アラートのしきい値 | 50% / 90% / 100% |
| 通知先 | 課金管理者のメールアドレス |

**2-3. 必要なAPIの有効化**

```bash
gcloud services enable sqladmin.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable storage.googleapis.com
```

**2-4. Gemini APIキーの取得**

1. https://aistudio.google.com/apikey にアクセス
2. 「APIキーを作成」をクリック
3. 表示されたAPIキーをメモする(後で.envに設定する)

**2-5. GCSバケットの作成**

```bash
gcloud storage buckets create gs://fictworks-rule-data-{プロジェクトID} \
  --location=asia-northeast1
```

就業規則ファイルをアップロードする。

```bash
gcloud storage cp data/fictworks_rules/*.md \
  gs://fictworks-rule-data-{プロジェクトID}/company_rule/
```

### 完了確認

- [ ] プロジェクトが作成されている
- [ ] 予算アラートが設定されている
- [ ] APIが全て有効化されている
- [ ] Gemini APIキーを取得している
- [ ] GCSに11ファイルがアップロードされている

---

## フェーズ3: ローカル開発環境構築

### 目的

ローカルPCで開発・テストができる環境を整える。

### 注意事項

**Python 3.12を使用すること。** Python 3.14はpydantic-coreのビルドエラーが発生するため使用不可。

### 作業内容

**3-1. Python 3.12のインストール**

```bash
# インストール済みか確認
py -3.12 --version
# → Python 3.12.x と表示されればOK

# インストールされていない場合
py install 3.12
```

**3-2. gcloud CLIのインストールとログイン**

1. https://cloud.google.com/sdk/docs/install からインストーラーをダウンロード
2. インストール後、ログインする

```bash
gcloud auth login
gcloud config set project {プロジェクトID}
gcloud auth application-default login
```

**3-3. プロジェクトフォルダの作成**

```bash
mkdir rag-rules-chatbot
cd rag-rules-chatbot

# フォルダ構成を作成
mkdir data data\fictworks_rules ingest app tests
```

**3-4. Python仮想環境の作成**

```bash
py -3.12 -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Mac/Linux
```

**3-5. requirements.txtの作成とインストール**

`requirements.txt` を以下の内容で作成する。

```
streamlit==1.45.0
cloud-sql-python-connector[pg8000]==1.13.0
sqlalchemy==2.0.36
google-cloud-aiplatform==1.71.1
google-generativeai==0.8.3
google-cloud-secret-manager==2.21.1
google-cloud-storage==2.19.0
python-dotenv==1.0.1
```

```bash
pip install -r requirements.txt
```

**3-6. .envファイルの作成**

`.env` を以下の内容で作成する(Gitignore対象)。

```
GEMINI_API_KEY=AIzaSy...（取得したAPIキー）
GOOGLE_CLOUD_PROJECT=my-project-rag-501004
```

### 完了確認

- [ ] `python --version` で Python 3.12.x と表示される
- [ ] `pip install` がエラーなく完了した
- [ ] .envファイルにGEMINI_API_KEYが設定されている

---

## フェーズ4: Cloud SQL構築

### 目的

ベクトルデータを格納するデータベースを用意する。

### 作業内容

**4-1. Cloud SQLインスタンスの作成**

```bash
gcloud sql instances create rag-rules-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=asia-northeast1 \
  --storage-size=10 \
  --storage-type=HDD \
  --root-password={任意のパスワード}
```

**⚠️ 作成に5〜10分かかる。完了まで待つ。**

**4-2. データベースとユーザーの作成**

```bash
gcloud sql databases create rag_db --instance=rag-rules-db

gcloud sql users create rag_user \
  --instance=rag-rules-db \
  --password={任意のパスワード}
```

**4-3. pgvector拡張とテーブルの作成**

Cloud SQL Studioで以下のSQLを実行する(ブラウザ操作)。

1. https://console.cloud.google.com/sql/instances にアクセス
2. `rag-rules-db` → Cloud SQL Studio
3. データベース: `rag_db` / ユーザー: `rag_user` でログイン
4. 以下のSQLを実行する

```sql
-- pgvector拡張を有効化
CREATE EXTENSION IF NOT EXISTS vector;

-- チャンク格納テーブルを作成
CREATE TABLE rule_chunks (
    id SERIAL PRIMARY KEY,
    source_file VARCHAR(255) NOT NULL,
    chapter_title VARCHAR(255),
    article_no VARCHAR(50),
    article_title VARCHAR(255),
    content TEXT NOT NULL,
    embedding VECTOR(768) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

-- 類似度検索用インデックスを作成
-- (768次元はivfflatの2000次元制限内のため使用可能)
CREATE INDEX idx_rule_chunks_embedding
    ON rule_chunks USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 10);
```

**4-4. 接続情報をメモする**

| 項目 | 値 |
|---|---|
| インスタンス接続名 | `{プロジェクトID}:asia-northeast1:rag-rules-db` |
| データベース名 | `rag_db` |
| ユーザー名 | `rag_user` |
| パスワード | 4-1で設定したもの |

### コスト管理(重要)

使用しない時間はインスタンスを停止する。

```bash
# 停止(課金が止まる)
gcloud sql instances patch rag-rules-db --activation-policy=NEVER

# 起動(翌日の作業開始時)
gcloud sql instances patch rag-rules-db --activation-policy=ALWAYS
```

### 完了確認

- [ ] `gcloud sql instances describe rag-rules-db` で `state: RUNNABLE` が表示される
- [ ] Cloud SQL Studio で `SELECT COUNT(*) FROM rule_chunks;` が `0` を返す

---

## フェーズ5: データ取り込みパイプライン実装

### 目的

就業規則のMarkdownファイルを読み込み、条文単位に分割してベクトル化し、Cloud SQLに格納するバッチ処理を実装する。このフェーズが完了すると検索の準備が整う。

### 作業内容

**5-1. chunker.py の実装**

Markdownを `## 第n条(タイトル)` の見出し単位で分割する。

```python
# ingest/chunker.py
import re

def parse_markdown_content(filename: str, text: str) -> list[dict]:
    """Markdownテキストを条文単位でチャンク分割する"""

    # 章タイトルの抽出(# 第n章 ...)
    chapter_match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    chapter_title = chapter_match.group(1).strip() if chapter_match else "不明な章"

    # 条文見出しの検出(## 第n条(...))
    pattern = r"^##\s+(第\d+条)(.*)$"
    matches = list(re.finditer(pattern, text, re.MULTILINE))

    chunks = []
    for i, match in enumerate(matches):
        article_no = match.group(1)
        article_title = match.group(2).strip().strip("()")
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        content = text[start:end].strip()

        chunks.append({
            "source_file": filename,
            "chapter_title": chapter_title,
            "article_no": article_no,
            "article_title": article_title if article_title else None,
            "content": content
        })

    return chunks
```

**5-2. embedder.py の実装**

**⚠️ 重要な注意事項:**
- `models/gemini-embedding-001` を使用すること(他のモデル名は404エラーになる)
- `output_dimensionality=768` を必ず指定すること(未指定時は3072次元が返りDBとミスマッチになる)
- Vertex AI SDKは使用しないこと(Python 3.12環境で全ての入力に同一ベクトルを返す不具合あり)

```python
# ingest/embedder.py
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def get_embedding(text: str) -> list[float]:
    """Gemini APIで768次元ベクトルを取得する"""
    result = genai.embed_content(
        model="models/gemini-embedding-001",
        content=text,
        task_type="retrieval_document",
        output_dimensionality=768    # ← 必須: 未指定時は3072次元になる
    )
    return result["embedding"]
```

**5-3. ingest.py の実装**

```python
# ingest/ingest.py
import os
import sqlalchemy
from google.cloud.sql.connector import Connector
from google.cloud import storage
from ingest.chunker import parse_markdown_content
from ingest.embedder import get_embedding

BUCKET_NAME = "fictworks-rule-data-{プロジェクトID}"
INSTANCE_CONNECTION_NAME = "{プロジェクトID}:asia-northeast1:rag-rules-db"
DB_USER = "rag_user"
DB_PASS = "{設定したパスワード}"
DB_NAME = "rag_db"

def get_engine():
    connector = Connector()
    def getconn():
        return connector.connect(
            INSTANCE_CONNECTION_NAME, "pg8000",
            user=DB_USER, password=DB_PASS, db=DB_NAME,
        )
    return sqlalchemy.create_engine("postgresql+pg8000://", creator=getconn)

def main():
    print("[INFO] 取り込み開始")

    # GCSからファイル取得
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blobs = list(bucket.list_blobs(prefix="company_rule/"))

    all_chunks = []
    for blob in blobs:
        if not blob.name.endswith(".md"):
            continue
        if "00_概要_目次" in blob.name:
            continue
        filename = os.path.basename(blob.name)
        text = blob.download_as_text(encoding="utf-8")
        chunks = parse_markdown_content(filename, text)
        all_chunks.extend(chunks)
        print(f"[INFO] {filename}: {len(chunks)} チャンク")

    print(f"[INFO] 総チャンク数: {len(all_chunks)} 件")

    engine = get_engine()
    with engine.connect() as conn:
        conn.execute(sqlalchemy.text("TRUNCATE TABLE rule_chunks;"))
        success = 0
        for chunk in all_chunks:
            try:
                embedding = get_embedding(chunk["content"])
                conn.execute(
                    sqlalchemy.text("""
                        INSERT INTO rule_chunks
                        (source_file, chapter_title, article_no, article_title, content, embedding)
                        VALUES (:source_file, :chapter_title, :article_no, :article_title, :content, :embedding)
                    """),
                    {**chunk, "embedding": str(embedding)}
                )
                success += 1
                print(f"  [{success}] {chunk['source_file']} {chunk['article_no']}")
            except Exception as e:
                print(f"[WARNING] スキップ: {e}")
        conn.commit()

    print(f"\n[SUCCESS] 登録完了: {success} / {len(all_chunks)} 件")

if __name__ == "__main__":
    main()
```

**5-4. バッチ実行**

```bash
python -m ingest.ingest
```

**5-5. 動作確認**

Cloud SQL Studioで確認する。

```sql
SELECT COUNT(*) FROM rule_chunks;
-- → 82 が返れば成功

SELECT source_file, article_no, article_title
FROM rule_chunks
LIMIT 5;
```

### 完了確認

- [ ] `python -m ingest.ingest` が82/82件で完了する
- [ ] Cloud SQLのCOUNT(*)が82を返す
- [ ] **このバッチは再実行を避ける(APIクォータ消費のため)**

---

## フェーズ6: バックエンド実装

### 目的

類似検索・回答生成・RAGパイプラインをPythonで実装する。

### 作業内容

**6-1. db.py の実装**

```python
# app/db.py
import sqlalchemy
from google.cloud.sql.connector import Connector

INSTANCE_CONNECTION_NAME = "{プロジェクトID}:asia-northeast1:rag-rules-db"
DB_USER = "rag_user"
DB_PASS = "{設定したパスワード}"
DB_NAME = "rag_db"

_engine = None

def get_engine():
    global _engine
    if _engine is None:
        connector = Connector()
        def getconn():
            return connector.connect(
                INSTANCE_CONNECTION_NAME, "pg8000",
                user=DB_USER, password=DB_PASS, db=DB_NAME,
            )
        _engine = sqlalchemy.create_engine("postgresql+pg8000://", creator=getconn)
    return _engine

def search_similar_chunks(query_embedding: list[float], top_k: int = 3) -> list[dict]:
    """pgvectorでコサイン類似度の高いチャンクを検索する"""
    vector_str = "[" + ",".join(str(v) for v in query_embedding) + "]"
    sql = sqlalchemy.text("""
        SELECT source_file, chapter_title, article_no, article_title, content,
               1 - (embedding <=> CAST(:vec AS vector)) AS similarity
        FROM rule_chunks
        ORDER BY embedding <=> CAST(:vec AS vector)
        LIMIT :top_k
    """)
    results = []
    with get_engine().connect() as conn:
        rows = conn.execute(sql, {"vec": vector_str, "top_k": top_k})
        for r in rows:
            # pg8000はインデックスアクセスを使用(属性アクセス不可)
            results.append({
                "source_file": r[0],
                "chapter_title": r[1],
                "article_no": r[2],
                "article_title": r[3],
                "content": r[4],
                "similarity": float(r[5]),
            })
    return results
```

**6-2. llm_client.py の実装**

**⚠️ 重要な注意事項:**
- `gemini-2.5-flash-lite` を使用すること
- `gemini-2.0-flash` は無料枠クォータ超過が発生するため使用しない
- 利用可能なモデルは `genai.list_models()` で確認できる

```python
# app/llm_client.py
import os
import time
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def generate_answer(question: str, contexts: list[dict]) -> str:
    """検索結果をコンテキストとしてGeminiに回答を生成させる"""
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-2.5-flash-lite")

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
            return model.generate_content(prompt).text
        except Exception as e:
            if attempt == 2:
                raise RuntimeError(f"Gemini API呼び出し失敗: {e}")
            time.sleep(3)
```

**6-3. rag_service.py の実装**

```python
# app/rag_service.py
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from ingest.embedder import get_embedding
from app.db import search_similar_chunks
from app.llm_client import generate_answer

def answer_question(question: str) -> dict:
    """質問に対してRAGパイプラインで回答を生成する"""
    if not question or not question.strip():
        raise ValueError("質問を入力してください。")

    # Step1: 質問をベクトル化
    query_embedding = get_embedding(question)

    # Step2: 類似チャンクを検索
    contexts = search_similar_chunks(query_embedding, top_k=3)

    # Step3: 類似度が低いチャンクを除外
    contexts = [c for c in contexts if c["similarity"] >= 0.5]

    # Step4: 該当なしの場合はフォールバック
    if not contexts:
        return {
            "answer": "就業規則内に関連する情報が見つかりませんでした。",
            "sources": []
        }

    # Step5: Geminiで回答生成
    answer = generate_answer(question, contexts)
    sources = [
        {
            "source_file": c["source_file"],
            "article_no": c["article_no"],
            "article_title": c["article_title"],
        }
        for c in contexts
    ]
    return {"answer": answer, "sources": sources}
```

**6-4. バックエンドの動作確認**

テストスクリプトで確認する。

```python
# tests/test_rag.py
from dotenv import load_dotenv
load_dotenv()
from app.rag_service import answer_question

questions = [
    "年次有給休暇は何日もらえますか？",
    "試用期間は何ヶ月ですか？",
    "今日の天気は？",  # フォールバック確認
]

for q in questions:
    print(f"Q: {q}")
    result = answer_question(q)
    print(f"A: {result['answer'][:100]}")
    print(f"出典: {result['sources']}")
    print()
```

```bash
python tests/test_rag.py
```

### 完了確認

- [ ] `test_rag.py` で「年次有給休暇」に第28条の内容が回答される
- [ ] 「試用期間」に第9条の内容が回答される
- [ ] 「今日の天気は？」でフォールバック回答が返る

---

## フェーズ7: Streamlit UI実装・ローカル動作確認

### 目的

Pythonだけでチャット画面を作り、ブラウザ上で動作確認する。

### 作業内容

**7-1. main.py の実装**

```python
# app/main.py
import streamlit as st
from app.rag_service import answer_question

st.set_page_config(
    page_title="就業規則チャットボット",
    page_icon="💼",
    layout="centered"
)

st.title("💼 就業規則チャットボット")
st.caption("株式会社フィクトワークス | 就業規則について何でも聞いてください")

# 会話履歴の初期化
if "messages" not in st.session_state:
    st.session_state.messages = []

# 過去の会話を表示
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg.get("sources"):
            with st.expander("📄 出典"):
                for s in msg["sources"]:
                    st.write(f"- {s['source_file']} {s['article_no']}({s['article_title']})")

# 質問入力と回答生成
if question := st.chat_input("就業規則について質問してください..."):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner("回答を生成中..."):
            try:
                result = answer_question(question)
                answer = result["answer"]
                sources = result["sources"]
            except Exception as e:
                answer = "エラーが発生しました。しばらくしてから再度お試しください。"
                sources = []

        st.write(answer)
        if sources:
            with st.expander("📄 出典"):
                for s in sources:
                    st.write(f"- {s['source_file']} {s['article_no']}({s['article_title']})")

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources
    })
```

**7-2. ローカルで起動**

```bash
streamlit run app/main.py
```

ブラウザが自動で `http://localhost:8501` を開く。

**7-3. 動作確認チェックリスト**

以下の質問を実際にチャット画面から送信して確認する。

| 質問 | 期待する結果 |
|---|---|
| 年次有給休暇は何日もらえますか？ | 勤続年数ごとの付与日数が回答される |
| 試用期間は何ヶ月ですか？ | 3か月(最大6か月)の内容が回答される |
| 出張手当はいくらですか？ | 日帰り2,000円・宿泊3,000円等が回答される |
| 副業はできますか？ | 事前申請が必要な旨が回答される |
| 今日の天気は？ | 「該当情報が見つかりませんでした」と回答される |

### 完了確認

- [ ] `streamlit run` でエラーなく起動する
- [ ] チャット画面が表示される
- [ ] 質問すると回答と出典が表示される

---

## フェーズ8: Cloud Runデプロイ

### 目的

ローカルで動いているアプリをGoogle Cloud上に公開し、誰でもブラウザからアクセスできる状態にする。

### 作業内容

**8-1. Dockerfileの作成**

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8080
EXPOSE 8080

CMD ["streamlit", "run", "app/main.py", \
     "--server.port=8080", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]
```

**8-2. .dockerignoreの作成**

```
venv/
.env
__pycache__/
*.pyc
.git/
tests/
data/
```

**8-3. Cloud Runへのデプロイ**

```bash
gcloud run deploy rag-rules-chatbot \
  --source . \
  --region asia-northeast1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY={APIキー},GOOGLE_CLOUD_PROJECT={プロジェクトID} \
  --min-instances 0 \
  --max-instances 1
```

**⚠️ `--min-instances 0` を必ず設定すること。アクセスがない時間の課金がゼロになる。**

**8-4. デプロイ完了の確認**

デプロイが完了すると以下のような公開URLが表示される。

```
Service URL: https://rag-rules-chatbot-xxxx-an.a.run.app
```

ブラウザでURLにアクセスし、チャット画面が表示されることを確認する。

**8-5. 最終動作確認**

公開URLから以下を確認する。

| 確認項目 | 内容 |
|---|---|
| チャット画面表示 | Streamlitの画面が表示されること |
| 回答生成 | 就業規則に関する質問に正しく回答されること |
| 出典表示 | 回答に条文番号とファイル名が表示されること |
| フォールバック | 関係ない質問に「該当情報なし」と返ること |

### 完了確認

- [ ] Dockerfileが作成されている
- [ ] `gcloud run deploy` がエラーなく完了する
- [ ] 公開URLでチャット画面が表示される
- [ ] 質問・回答・出典が正しく動作する

---

## 作業終了時の必須作業(コスト管理)

### 毎日の作業終了時

```bash
# Cloud SQLを停止(課金が止まる)
gcloud sql instances patch rag-rules-db --activation-policy=NEVER
```

### 翌日の作業開始時

```bash
# Cloud SQLを起動
gcloud sql instances patch rag-rules-db --activation-policy=ALWAYS
```

### プロジェクト完了後

```bash
# Cloud SQLインスタンスを削除(課金完全停止)
gcloud sql instances delete rag-rules-db

# GCSバケットを削除
gcloud storage rm -r gs://fictworks-rule-data-{プロジェクトID}

# Cloud Runサービスを削除(不要な場合)
gcloud run services delete rag-rules-chatbot --region asia-northeast1
```

---

## トラブルシューティング

### よくあるエラーと対処法

| エラー | 原因 | 対処法 |
|---|---|---|
| `pydantic-core` ビルドエラー | Python 3.14使用 | Python 3.12に切り替える |
| `psycopg2-binary` ビルドエラー | Python 3.12でビルド不可 | `pg8000`を使用する(cloud-sql-python-connectorに含まれる) |
| Vertex AI Embeddingが全て同じベクトルを返す | Python 3.12 + vertexai SDK不具合 | Gemini API(`google-generativeai`)に切り替える |
| `models/text-embedding-004` 404エラー | Gemini API v1betaで未対応 | `models/gemini-embedding-001`を使用する |
| `models/embedding-001` 404エラー | Gemini API v1betaで未対応 | `models/gemini-embedding-001`を使用する |
| Gemini回答生成が404エラー | モデル名が無効 | `genai.list_models()`で有効なモデルを確認する |
| Gemini回答生成が429エラー | 無料枠クォータ超過 | `gemini-2.5-flash-lite`に切り替える |
| VECTOR(3072)でivfflatインデックスエラー | pgvectorの上限(2000次元)超過 | `output_dimensionality=768`を指定して768次元にする |
| pg8000で属性アクセスエラー | pg8000はカラム名での属性アクセス不可 | `r[0]`, `r[1]`のインデックスアクセスを使用する |

### デバッグの基本手順

**検索が機能しない場合:**

1. Embeddingが正しく動いているか確認する
```bash
python tests/test_embedding.py
# → 2つの質問で異なるベクトルが返ること
```

2. DBのデータが正しく入っているか確認する(Cloud SQL Studio)
```sql
SELECT article_no, LEFT(embedding::text, 50) FROM rule_chunks LIMIT 3;
-- → 件ごとに異なる値が入っていること
```

3. 検索結果が正しいか確認する
```bash
python tests/test_search.py
# → 「年次有給休暇」に第28条が0.85以上の類似度でヒットすること
```

---

## Gemini APIの無料枠制限(2026年7月時点)

| モデル | リクエスト/分 | トークン/分 | リクエスト/日 |
|---|---|---|---|
| gemini-embedding-001 | 100 | 30,000 | 1,000 |
| gemini-2.5-flash-lite | 10 | 250,000 | 20 |

**ingest.pyの1回の実行で82回のEmbedding APIを消費する。** 再実行を避け、データは1回格納したら再利用すること。

---

## 学習ポイントまとめ

このプロジェクトで習得できる技術と概念は以下の通りである。

| カテゴリ | 習得内容 |
|---|---|
| RAGの仕組み | Embedding → ベクトル検索 → LLM生成の3ステップ |
| Google Cloud | Cloud SQL / Cloud Run / GCS / Secret Managerの操作 |
| pgvector | ベクトル格納・コサイン類似度検索・ivfflatインデックス |
| Gemini API | Embedding API・テキスト生成APIの両方の使い方 |
| Streamlit | PythonだけでWebアプリ・チャットUIを作る方法 |
| Docker | PythonアプリのDockerfile作成・Cloud Runデプロイ |
| コスト管理 | クラウドリソースの停止・削除・予算アラートの設定 |
| デバッグ | 「どの段階で壊れているか」を切り分けるテスト手法 |
