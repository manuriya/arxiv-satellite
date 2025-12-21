# coding: UTF-8
import os

from dotenv import load_dotenv

# Environment variables
load_dotenv(".env")

# API token
SLACK_API_TOKEN = [
    os.environ.get(key) for key in os.environ.keys() if "SLACK_API_TOKEN" in key
]
DEEPL_API_TOKEN = os.environ.get("DEEPL_API_TOKEN")
MS_TRANSLATE_KEY = os.environ.get("MS_TRANSLATE_KEY")
MS_TRANSLATE_REGION = os.environ.get("MS_TRANSLATE_REGION")
GEMINI_API_TOKEN = os.environ.get("GEMINI_API_TOKEN")
PROMPT = """
の論文を下記の項目に従って日本語で要約してください。
その際、項目の回答以外のメッセージは不要です。

## **研究の概要**

- 本研究の目的および主要な提案内容を簡潔に記述してください

## **先行研究との差異および優位性**

- 本研究が先行研究と比較して新規性を有する点や、優れている点を示してください

## **主要な技術・手法** 

- 本研究で採用された主要な技術や手法について説明してください

## **有効性の検証方法** 

- 本研究の有効性をどのように評価・検証したのか、具体的な実験手法や評価方法を記述してください。

## **議論および課題** 

- 研究成果や提案手法に関する議論点、制約、今後の課題について記載してください。

## **関連文献・推奨論文** 

- 本研究に関連する主要な参考文献や、次に読むべき論文を紹介してください
- 参考文献はタイトル, リンクを提示してください
- ただし、調査している論文と同じ論文は除外してください
- 3件程度を目安に提示してください

"""

# Slack channel
POST_CHANNEL = [
    os.environ.get(key) for key in os.environ.keys() if "POST_CHANNEL" in key
]

# RSS publisher
PUBLISH = dict(ArXiv="cs.CV", MDPI="remotesensing")

# Slack color list
COLOR = ["#d7003a", "#f6ad49", "#ffdb4f", "#00a381", "#89c3eb", "#bbc8e6", "#a59aca"]
