# test_search.py
import os
from dotenv import load_dotenv

# .envの読み込み
load_dotenv()

from ingest.embedder import get_embedding
from app.db import search_similar_chunks

def test_db_search(question: str):
    print(f"=== 検索テスト開始 ===")
    print(f"質問: {question}")
    
    # 1. 質問文をベクトル化
    try:
        query_embedding = get_embedding(question)
        print(f"-> ベクトル化成功 (次元数: {len(query_embedding)})")
    except Exception as e:
        print(f"-> ベクトル化失敗: {e}")
        return

    # 2. Cloud SQLから検索（上位5件を取得してみる）
    try:
        results = search_similar_chunks(query_embedding, top_k=5)
        print(f"-> DB検索完了 (取得件数: {len(results)})")
        print("-" * 60)
        
        for i, row in enumerate(results, 1):
            print(f"【上位 {i} 位】")
            print(f"  ファイル名: {row['source_file']}")
            print(f"  条文番号  : {row['article_no']} ({row['article_title']})")
            print(f"  コサイン類似度: {row['similarity']:.4f}")
            # 本文の先頭50文字だけ表示
            clean_content = row['content'].replace('\r', '').replace('\n', ' ')
            print(f"  本文一部  : {clean_content[:80]}...")
            print("-" * 60)
            
    except Exception as e:
        print(f"-> DB検索失敗: {e}")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    # テスト①: 本来なら「02_採用・人事.md」がヒットするべき質問
    test_db_search("試用期間は何ヶ月ですか？")
    
    # テスト②: 本来なら「04_休暇制度.md」や「05_給与・賞与.md」がヒットするべき質問
    test_db_search("有給休暇は何日もらえますか？")