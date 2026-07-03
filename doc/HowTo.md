# HowTo.md

# 就業規則RAGチャットボット（学習用）利用手順

このドキュメントでは、本プロジェクトの起動方法を説明します。

以下の2通りの方法があります。

- Dockerを使用しない（開発・デバッグ向け）
- Dockerを使用する（Cloud Runに近い実行環境）

---

# 前提条件

以下がインストール済みであること。

- Python 3.12
- Git
- Docker Desktop（Dockerを利用する場合）
- Google Cloud SDK（gcloud）
- Google Cloudプロジェクト設定済み
- Cloud SQL作成済み
- `.env`作成済み

---

# ディレクトリへ移動

```powershell
cd D:\AIM\202606\RAG
```

---

# 方法1 Dockerを使用しない（推奨）

開発中はこちらの方法を推奨します。

## ① 仮想環境を有効化

PowerShell

```powershell
.\venv\Scripts\Activate.ps1
```

有効になると

```
(venv) PS D:\AIM\202606\RAG>
```

と表示されます。

---

## ② ライブラリをインストール（初回のみ）

```powershell
pip install -r requirements.txt
```

---

## ③ Streamlit起動

```powershell
python -m streamlit run app/main.py
```

または

```powershell
streamlit run app/main.py
```

---

## ④ ブラウザでアクセス

```
http://localhost:8501
```

チャット画面が表示されれば成功です。

---

## ⑤ 終了

PowerShellで

```
Ctrl + C
```

---

# 方法2 Dockerを使用する

Cloud Runに近い環境で動作確認できます。

## ① Docker Desktopを起動

Docker Desktopを起動し、

```
Engine running
```

になっていることを確認します。

---

## ② Dockerイメージ作成

```powershell
docker build -t rag-rules-chatbot .
```

作成完了確認

```powershell
docker images
```

例

```
REPOSITORY          TAG
rag-rules-chatbot   latest
```

---

## ③ コンテナ起動

```powershell
docker run -p 8080:8080 -v "$env:APPDATA\gcloud:/root/.config/gcloud" -e GOOGLE_APPLICATION_CREDENTIALS=/root/.config/gcloud/application_default_credentials.json --env-file .env rag-rules-chatbot
```

---

## ④ ブラウザでアクセス

```
http://localhost:8080
```

---

## ⑤ コンテナ停止

実行中のPowerShellで

```
Ctrl + C
```

または

```powershell
docker stop <コンテナID>
```

---

# Docker便利コマンド

## 起動中コンテナ確認

```powershell
docker ps
```

---

## 停止済みも含め確認

```powershell
docker ps -a
```

---

## イメージ一覧

```powershell
docker images
```

---

## ログ確認

```powershell
docker logs <コンテナID>
```

---

## コンテナ削除

```powershell
docker rm <コンテナID>
```

---

## イメージ削除

```powershell
docker rmi rag-rules-chatbot
```

---

# Docker利用時の注意事項

Cloud SQL Python Connectorを利用する場合、ローカルDockerではGoogle Cloud認証情報（Application Default Credentials）が必要です。

ローカル（venv）では動作しても、Dockerでは以下のようなエラーが発生することがあります。

```
google.auth.exceptions.DefaultCredentialsError
```

これはDockerコンテナ内にGoogle Cloud認証情報が存在しないためです。

Cloud Runへデプロイした場合は、サービスアカウントが自動的に認証されるため、この設定は不要です。

---

# トラブルシューティング

## Streamlitが起動しない

ライブラリを再インストールします。

```powershell
pip install -r requirements.txt
```

---

## ポート8501が使用中

別ポートで起動できます。

```powershell
streamlit run app/main.py --server.port 8502
```

---

## Dockerで起動しない

コンテナログを確認します。

```powershell
docker logs <コンテナID>
```

---

## コンテナID確認

```powershell
docker ps -a
```

---

# 開発時の推奨手順

通常の開発は以下の流れを推奨します。

```
venv起動
    ↓
コード修正
    ↓
Streamlitで確認
    ↓
動作確認
    ↓
Docker Build
    ↓
Docker動作確認
    ↓
Cloud Runへデプロイ
```

Dockerは最終確認用として利用すると、開発効率が向上します。