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
自分専用の情報を知らない。


例:

質問:

株式会社フィクトワークスの有給ルールを教えて


LLM:

一般的な労務知識は回答できるが、
会社独自の規則は知らない。



LLMが知らない情報:

- 社内資料
- 自社マニュアル
- 過去資料
- 非公開データ


この問題を解決する仕組みがRAG。




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





# RAGの基本処理

RAGには大きく2つの処理がある。


1. データ登録時

2. 質問時



# 1. データ登録時の処理



## 文書準備


対象:

- Markdown
- PDF
- TXT
- Word


今回:

就業規則.md


↓

文章取得



## Chunk分割


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
- 必要な部分だけ取得するため



## Embedding化


文章を数字（ベクトル）へ変換する。



例:


有給休暇の取得方法


↓

[0.234,0.556,0.921]



この数字を使って、

「意味が近い文章」

を検索する。



## Vector Databaseへ保存


Vector Database:

検索用データベース



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





# 2. 質問時のRAG処理



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



RAG:

参考情報:

03_勤務時間・休憩・休日.md


内容:

テレワーク制度について...



↓

LLM


↓

回答生成




# LM Studioとは


- PC上でLLMを動かすツール
- ローカルLLM実行環境



## LM Studioの位置づけ


LM Studioは主に、

- 開発確認
- RAG動作確認
- プロンプト調整

で使用する。



## LM Studio構成


質問


↓

自分のPC


↓

LM Studio


↓

LLM


↓

回答





# LM Studioの役割



RAG:

必要な情報を検索する



↓

LM Studio:

検索結果をもとに文章を作る




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

× RAG検索




## LM Studioがやること


○ 文章生成

○ 質問への回答





# Google Cloudとは


- クラウド上のコンピュータ環境
- サーバやAIサービスを利用する場所



イメージ:


自分のPC:

開発環境


Google Cloud:

本番サービスを動かす環境





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

- 就業規則ファイル保存





## Vector Database


RAG検索用データベース



流れ:


文章

↓

Embedding

↓

ベクトル保存

↓

検索





## Vertex AI


Google Cloud上のAIサービス


役割:


- LLM利用
- 回答生成



本番環境では、

LM Studioの代わりに利用する。




# RAG・LM Studio・Google Cloudの関係



## 開発・確認環境

Markdown

↓

RAG

↓

Vector DB

↓

LM Studio

↓

回答




目的:

- RAG動作確認
- 開発



---


## 本番環境

Markdown

↓

Cloud Storage

↓

Embedding

↓

Vector Database

↓

RAG

↓

Vertex AI

↓

回答




目的:

- Google Cloud上でサービス提供





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

LLM

↓

回答生成

↓

表示





# 開発から本番までの流れ



## Step1 開発確認


ローカル:


Markdown

↓

RAG

↓

Vector DB

↓

LM Studio

↓

回答




## Step2 Google Cloud移行


変更:


LM Studio

↓

Vertex AI



保存:


ローカルファイル

↓

Cloud Storage




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

LLM接続





data/


└ company_rule/





frontend/


└ app.py

