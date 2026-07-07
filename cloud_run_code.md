# Cloud Run デプロイ手順

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

## 環境変数の設定
- .env は Cloud Runでは使用されない
1. Cloud Runの設定
2. 新しいリビジョンの編集とデプロイ
3. コンテナの編集 → 変数とシークレット → 環境変数
4. 名前と値を入力（例: 名前「GEMINI_API_KEY」 値「xxx」）

## URLを確認
```powershell
gcloud run services describe rag-rules-chatbot --region asia-northeast1 --format="value(status.url)"
```

## URL
- 以下にアクセスして利用
```
https://rag-rules-chatbot-951526636814.asia-northeast1.run.app
```

