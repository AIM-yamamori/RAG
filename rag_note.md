# LLM・RAG・LM Studio・Google Cloud 基礎メモ


# LLMとは

LLM (Large Language Model)

文章を理解して回答を生成するAIモデル。


## 例

質問:
    日本の首都は？

LLM:
    東京です。


## LLMができること

- 質問回答
- 文章生成
- 要約
- 翻訳
- コード生成


## LLMの弱点

LLMは学習していない情報や、
社内限定の情報を知らない。


例:

質問:

2026年の自社ルールを教えて


LLM:

一般的な知識なら回答できるが、
自社独自のルールは知らない


LLMが知らない情報:

- 社内資料
- 自社PDF
- 過去資料
- マニュアル
- 非公開データ


この問題を解決する方法がRAG。



# RAGとは

RAG:

Retrieval Augmented Generation

検索拡張生成


## 目的

LLMに外部資料を検索させ、
必要な情報を渡して回答させる仕組み。


## 通常のLLM

質問

↓

LLM

↓

回答


## RAG

質問

↓

資料検索

↓

必要な情報取得

↓

LLM

↓

回答



# RAGの処理


## 1. 文書を準備

対象:

- PDF
- Markdown
- TXT
- Word


例:

就業規則.md

↓

文章化

↓

分割



## 2. Chunk分割

文章を検索しやすいサイズに分割する。


例:

元:

04_休暇制度.md

5000文字


↓

chunk1

年次有給休暇について...


chunk2

育児休業について...


目的:

- 検索精度向上
- LLMへ渡す情報量を調整



## 3. Embedding化

文章を数字（ベクトル）へ変換する。


例:

有給休暇の取得方法

↓

[0.234,0.556,0.921]


この数字を使って、

「意味が近い文章」

を検索する。



## 4. Vector Databaseへ保存


Vector Database:

検索専用データベース


例:


Vector DB


[0.234,0.556]

↓

04_休暇制度.md

chunk1



[0.812,0.332]

↓

09_情報セキュリティ.md

chunk3




# 質問時のRAG処理


質問:

テレワークのルールを教えて



## ① 質問をEmbedding化


テレワークのルール

↓

[0.245,0.551]



## ② Vector検索


意味が近い文章を探す。


結果:

03_勤務時間・休憩・休日.md

テレワーク制度について...



## ③ LLMへ渡す


検索結果:

参考資料:

03_勤務時間・休憩・休日.md


内容:

テレワーク制度について...



↓

LLM


↓

回答生成




# LM Studioとは


- PC上でLLMを動かすための環境
- ローカルLLM実行ツール


通常:

質問

↓

クラウドAI

↓

回答



LM Studio:

質問

↓

自分のPC

↓

LLM

↓

回答



# LM Studioの役割


RAGでは役割分担する。


RAG:

必要な情報を探す


↓

LM Studio:

情報をもとに文章を作成する



例:


RAG:

参考情報:

輸入者:
ABC Trading

原産国:
China



↓

LM Studio:

回答:

輸入者はABC Tradingです。

原産国はChinaです。




## LM Studioがやらないこと


× PDF検索

× ファイル管理

× データ保存



## LM Studioがやること


○ 文章生成

○ 質問への回答




# Google Cloudとは


- クラウド上のコンピュータ環境
- サーバやサービスを利用できる場所


イメージ:


自分のPC:

小さいコンピュータ


Google Cloud:

大きなコンピュータ環境を借りる




# Google Cloudの役割


## Cloud Storage


ファイル保存場所


例:


bucket:

documents/

├ 00_概要_目次.md

├ 01_総則.md

├ 02_採用・人事.md




役割:

- データ保管



## Document AI


文書解析サービス


例:

PDF

↓

文字・表抽出

↓

データ化




## Vector Database


RAG検索用DB


流れ:


文章

↓

Embedding

↓

ベクトル保存

↓

検索




# RAG・LM Studio・Google Cloudの関係


RAG:

- 必要な情報を探す仕組み


LM Studio:

- AI回答を作るエンジン


Google Cloud:

- データ保存やクラウド基盤




# 今回作成予定のシステム


## 目的

就業規則Markdownを知識データとして、

質問に回答する社内AIチャットを作成する。



## 使用データ


検索対象:

架空会社の就業規則

Markdown 11ファイル



00_概要_目次.md

01_総則.md

02_採用・人事.md

03_勤務時間・休憩・休日.md

04_休暇制度.md

05_給与・賞与.md

06_福利厚生.md

07_服務規律.md

08_懲戒.md

09_情報セキュリティ.md

10_経費・出張規程.md




# システム全体構成


社員

↓

質問入力

↓

Web画面

(Streamlit / React)

↓

FastAPI

↓

RAG

↓

Vector検索

↓

関連文章取得

↓

LM Studio

↓

回答生成

↓

表示




# データ登録時の流れ


Markdown

↓

Google Cloud Storage保存

↓

読み込み

↓

Chunk分割

↓

Embedding

↓

Vector Database保存




# 質問時の流れ


質問

↓

質問をEmbedding化

↓

Vector検索

↓

関連文章取得

↓

LM Studioへ渡す

↓

回答生成

↓

ユーザー表示




# 実装フォルダ構成イメージ


rag-system/


backend/


├ main.py


├ rag/


├ loader.py

Markdown読み込み


├ splitter.py

Chunk分割


├ embedding.py

ベクトル化


├ search.py

Vector検索


└ llm.py

LM Studio接続



data/


└ company_rule/



frontend/


└ app.py




# 今後学ぶ順番


1. Markdown読み込み

2. Chunk分割

3. Embedding

4. Vector Database

5. LM Studio API接続

6. RAG処理実装

7. FastAPI連携

8. Google Cloud連携