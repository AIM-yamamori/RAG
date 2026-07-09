# イメージ作成
```powershell
docker build -t rag-rules-chatbot .
```

# 起動
- Cloud SQL Python Connector が Google Cloud の認証情報を見つけられない
- dockerを使用しないローカル環境ではWindows側の認証情報（Application Default Credentials: ADC）を利用できている
- `"$env:APPDATA\gcloud:/root/.config/gcloud" -e GOOGLE_APPLICATION_CREDENTIALS=/root/.config/gcloud/application_default_credentials.json`
- 上の部分でApplication Default Credentials をコンテナへ渡す
```powershell
docker run -p 8080:8080 -v "$env:APPDATA\gcloud:/root/.config/gcloud" -e GOOGLE_APPLICATION_CREDENTIALS=/root/.config/gcloud/application_default_credentials.json --env-file .env rag-rules-chatbot
```

# 起動中確認
```powershell
docker ps
```

# 停止済みも確認
```powershell
docker ps -a
```

# ログ確認
```powershell
docker logs <コンテナID>
```

# 停止
```powershell
docker stop <コンテナID>
```

# 削除
```powershell
docker rm <コンテナID>
```