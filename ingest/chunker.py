import os
import re

def parse_markdown_content(filename: str, text: str) -> list[dict]:
    """Markdownテキストを読み込み、条文（## 第n条）単位でチャンク分割する"""
    
    # 章タイトルの抽出 (# 第n章 ...)
    chapter_match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    chapter_title = chapter_match.group(1).strip() if chapter_match else "不明な章"

    # 条文見出しの検出 (## 第n条(タイトル) または ## 第n条)
    pattern = r"^##\s+(第\d+条)(.*)$"
    matches = list(re.finditer(pattern, text, re.MULTILINE))

    chunks = []
    for i, match in enumerate(matches):
        article_no = match.group(1)
        article_title = match.group(2).strip().strip("()") # カッコを外す
        start = match.start()
        
        # 次の条文の開始位置、もしくはファイル末尾までを本文とする
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