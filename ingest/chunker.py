import os
import re



# Markdownファイルを条文単位に分割する関数
#
# 処理:
# Markdown
# ↓
# 第n条ごとに分割
# ↓
# チャンク(検索単位)作成
#
def parse_markdown_content(
    filename: str,
    text: str
) -> list[dict]:



    # 章タイトル取得
    #
    # 例:
    # # 第1章 総則
    #
    # ↓
    # 第1章 総則
    #
    chapter_match = re.search(
        r"^#\s+(.+)$",
        text,
        re.MULTILINE
    )


    chapter_title = (
        chapter_match.group(1).strip()
        if chapter_match
        else "不明な章"
    )



    # 条文見出しを検索
    #
    # 例:
    # ## 第28条 年次有給休暇
    #
    # ## 第29条 休暇申請
    #
    pattern = r"^##\s+(第\d+条)(.*)$"


    matches = list(
        re.finditer(
            pattern,
            text,
            re.MULTILINE
        )
    )



    chunks = []


    # 条文ごとに分割
    for i, match in enumerate(matches):


        # 条文番号取得
        #
        # 第28条
        article_no = match.group(1)



        # 条文タイトル取得
        #
        # 年次有給休暇
        article_title = (
            match.group(2)
            .strip()
            .strip("()")
        )



        # 条文開始位置
        start = match.start()



        # 次の条文までを本文とする
        #
        # 第28条
        # ↓
        # 第29条直前まで
        #
        end = (
            matches[i + 1].start()
            if i + 1 < len(matches)
            else len(text)
        )


        # 条文本文取得
        content = text[start:end].strip()



        # 1チャンクとして保存
        chunks.append({

            # 元ファイル名
            "source_file": filename,

            # 章タイトル
            "chapter_title": chapter_title,

            # 条文番号
            "article_no": article_no,

            # 条文タイトル
            "article_title":
                article_title
                if article_title
                else None,

            # 条文本文
            "content": content
        })


    return chunks