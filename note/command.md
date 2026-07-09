# コマンド

## venv仮想環境有効化
- プロジェクトのルートで
```powershell
.\venv\Scripts\activate.ps1
```

## venv仮想環境終了
```powershell
deactivate
```

---

## GCSへ.mdをアップロード
- 就業規則md更新時など
```powershell
gcloud storage cp .\data\company_rule\*.md gs://fictworks-rule-data-501004/company_rule/
```

## RAG登録バッチ実行
1. Cloud Strageから.md読み込み
2. テキスト抽出
3. チャンク分割
4. 各チャンクのEmbeddingを生成
5. EmbeddingとチャンクをVector Searchへ登録する
```powershell
python -m ingest.ingest
```

## 質問テストするとき
- FastAPI起動
```powershell
uvicorn app.main:app --reload
```
- 以下を別PowerShellで
```powershell
curl http://localhost:8000/api/health
```
- 以下が結果
```json
{
 "status":"ok"
}
```

## Cloud SQL 検索テストを実行
- 「Embedding生成 → Cloud SQL検索 → 結果表示」が動くテスト
```powershell
python test_search.py
```

## APIで質問確認
- PowerShellで
```powershell
curl -X POST http://localhost:8000/api/chat -H "Content-Type: application/json" -d '{"question":"有給休暇は何日ですか"}'
```

## DB確認
- Cloud SQL接続：
```powershell
gcloud sql connect rag-rules-db --user=rag_user
```
- DB:
```sql
\c rag_db
```
- 件数確認:
```sql
SELECT COUNT(*) FROM rule_chunks;
```

---

## Cloud SQL 停止
- 常時課金を防ぐ
- インスタンスは停止し、ユーザーが明示的に起動するまで再起動されません。
```powershell
gcloud sql instances patch rag-rules-db --activation-policy=NEVER
```

## Cloud SQL 起動
```powershell
gcloud sql instances patch rag-rules-db --activation-policy=ALWAYS
```

## Cloud SQL 状態確認
```powershell
gcloud sql instances describe rag-rules-db --format="value(state)"
```