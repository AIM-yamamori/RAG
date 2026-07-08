# 就業規則チャットボット

社内ドキュメント（架空企業「株式会社フィクトワークス」の就業規則・ルールブック）に対して自然言語で質問すると、関連する条文を検索し、根拠（出典）を示しながら回答するRAG（Retrieval-Augmented Generation）システムです。

フロントエンドからバックエンドまで**Pythonのみ（JavaScript一切不使用）**で実装されており、Google CloudおよびRAGアーキテクチャの学習、コストを抑えた運用の検証を目的としたプロジェクトです。

![GitHub license](https://img.shields.io/github/license/AIM-yamamori/RAG)
![GitHub star](https://img.shields.io/github/stars/AIM-yamamori/RAG)

## 主な機能 (Features)

- **自然言語による質問応答**: 「年次有給休暇は何日もらえますか？」などの質問に、就業規則に基づき自動回答
- **根拠（出典）の明示**: 回答のベースとなった「ファイル名」や「条文番号」をアコーディオン（`st.expander`）で折りたたみ表示
- **フォールバック対応**: 就業規則内に該当情報がない場合は、推測せず「該当する情報が見つかりませんでした」と安全に回答
- **シンプルなチャットUI**: Streamlit標準のチャットコンポーネントを採用し、直感的な対話が可能
- **会話履歴の保持**: 同一セッション内での会話の流れを画面上に保持

## 🛠 システム構成・使用技術

Google Cloud環境をベースに、学習目的のためにコストと安定性を最優先した構成を採用しています。

- **フロントエンド / Webアプリ**: Streamlit (v1.45.0)
- **ホスティング基盤**: Cloud Run (アクセスがない時はインスタンス数0に自動スケール)
- **Embedding API**: Gemini API (`models/gemini-embedding-001` / 768次元に固定)
- **LLM (回答生成)**: Gemini API (`gemini-2.5-flash-lite` / 無料枠内で安定動作)
- **ベクトルデータベース**: Cloud SQL for PostgreSQL 15 + `pgvector`拡張 (db-f1-micro)
- **ファイルストレージ**: Google Cloud Storage (就業規則Markdownの格納)
- **秘密情報管理**: Secret Manager / 環境変数 (`.env`)

## 📂 ディレクトリ構成

```text
rag-rules-chatbot/
├── README.md
├── requirements.txt              # Python依存ライブラリ
├── .env                          # 環境変数 (Gitignore対象)
├── .env.example                  # 環境変数サンプル
├── Dockerfile                    # Cloud Runデプロイ用 (streamlit run 起動)
├── data/
│   └── fictworks_rules/          # 就業規則Markdownファイル (全11ファイル、82条)
├── ingest/
│   ├── ingest.py                 # データ取り込みバッチのエントリポイント
│   ├── chunker.py                # Markdownの条文単位チャンク分割処理
│   └── embedder.py               # ベクトル化処理 (Gemini API)
├── app/
│   ├── main.py                   # Streamlitアプリのエントリポイント
│   ├── rag_service.py            # 検索〜回答生成のコアロジック
│   ├── db.py                     # Cloud SQL接続・pgvector検索処理 (pg8000使用)
│   └── llm_client.py             # Gemini API呼び出し処理
├── infra/
│   ├── setup_cloudsql.sql        # pgvector有効化・テーブル作成SQL
│   └── deploy.sh                 # Cloud Runデプロイ用シェルスクリプト
└── tests/
    ├── test_search.py            # ベクトル検索単体テスト
    ├── test_embedding.py         # Embedding API単体テスト
    └── test_rag_service.py       # RAGパイプライン統合テスト
```

## セットアップ・使い方 (Installation & Usage)

### 1. リポジトリをクローン

```powershell
git clone https://github.com/AIM-yamamori/RAG.git
cd リポジトリ名
```

### 2. 依存関係のインストール

- 仮想環境を成
- 仮想環境の有効化
- requirements.txt に記載のパッケージをインストール

```powershell
PowerShell -ExecutionPolicy Bypass -File .\venv_setup.ps1
```

### 3. .envの設定
以下の項目を入力
- GEMINI_API_KEY
- DB_USER
- DB_PASS
- DB_NAME
- INSTANCE_CONNECTION_NAME
- BUCKET_NAME

### 4. 実行

#### A. ローカルVENVで実行

```powershell
streamlit run app\main.py 
```

[http://localhost:8501にアクセス](http://localhost:8501)

#### B. ローカルDockerで実行

```powershell
docker run -p 8080:8080 -v "$env:APPDATA\gcloud:/root/.config/gcloud" -e GOOGLE_APPLICATION_CREDENTIALS=/root/.config/gcloud/application_default_credentials.json --env-file .env rag-rules-chatbot
```

[http://localhost:8501にアクセス](http://localhost:8501)

#### C. Cloud Runで実行

- 公開リンクにアクセス

### 5. データベースの更新
- 就業規則mdが更新されたときなど
```python
python -m ingest.ingest.py
```

### 6. Cloud Runデプロイ

## プロジェクトを選択
```powershell
gcloud config set project my-project-rag-501004
```

## 確認
```powershell
gcloud config list
```

## Dockerイメージをビルド
```powershell
docker build -t rag-rules-chatbot .
```

## Artifact Registry用にタグ付け
```powershell
docker tag rag-rules-chatbot asia-northeast1-docker.pkg.dev/my-project-rag-501004/cloud-run-source-deploy/rag-rules-chatbot:latest
```

## Artifact RegistryへPush
- 初回のみ:
```powershell
gcloud auth configure-docker asia-northeast1-docker.pkg.dev
```
- イメージをPush:
```powershell
docker push asia-northeast1-docker.pkg.dev/my-project-rag-501004/cloud-run-source-deploy/rag-rules-chatbot:latest
```

## Cloud Runへデプロイ
```powershell
gcloud run deploy rag-rules-chatbot --image asia-northeast1-docker.pkg.dev/my-project-rag-501004/cloud-run-source-deploy/rag-rules-chatbot:latest --region asia-northeast1 --allow-unauthenticated
```