import os
import time
from google.cloud import aiplatform
from vertexai.language_models import TextEmbeddingModel

def get_embedding(text: str) -> list[float]:
    """Vertex AIを用いて768次元のベクトルを取得する（task_typeなし版）"""
    project = os.getenv("GOOGLE_CLOUD_PROJECT", "my-project-rag-501004")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    
    aiplatform.init(project=project, location=location)
    model = TextEmbeddingModel.from_pretrained("text-embedding-004")
    
    for attempt in range(1, 4):
        try:
            # 【重要】task_type を指定せず、プレーンな文字列リストとして渡す
            embeddings = model.get_embeddings([text])
            
            # 無料枠のレートリミット対策として一応0.2秒待機
            time.sleep(0.2)
            return embeddings[0].values
        except Exception as e:
            if attempt == 3:
                print(f"[ERROR] ベクトル化に3回失敗しました: {text[:30]}...")
                raise e
            wait_time = 2 ** attempt
            print(f"[WARNING] APIエラーのため {wait_time}秒後にリトライします: {e}")
            time.sleep(wait_time)