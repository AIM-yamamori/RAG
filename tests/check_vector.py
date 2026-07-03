# check_vector.py
import os
from dotenv import load_dotenv
load_dotenv()

from ingest.embedder import get_embedding
from app.db import get_engine
import sqlalchemy

print("=== ① ベクトル化テスト ===")
v1 = get_embedding("試用期間は何ヶ月ですか？")
v2 = get_embedding("有給休暇は何日もらえますか？")

print(f"質問1のベクトル(先頭5要素): {v1[:5]}")
print(f"質問2のベクトル(先頭5要素): {v2[:5]}")
if v1[:5] == v2[:5]:
    print("❌ 警告: 違う質問なのに生成されたベクトルが完全に一致しています（原因①）")
else:
    print("✅ 正常: 質問によって異なるベクトルが生成されています。")

print("\n=== ② DBデータ確認テスト ===")
engine = get_engine()
with engine.connect() as conn:
    # 最初の3件のベクトルをそのまま文字列として取得して比較してみる
    sql = sqlalchemy.text("SELECT id, source_file, article_no, LEFT(embedding::text, 80) as vec_str FROM rule_chunks LIMIT 3")
    rows = conn.execute(sql).fetchall()
    for r in rows:
        print(f"ID: {r.id} | {r.source_file} {r.article_no} | ベクトル先頭: {r.vec_str}...")