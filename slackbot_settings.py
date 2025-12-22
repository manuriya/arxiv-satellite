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

## *研究の概要*
## *先行研究との差異および優位性*
## *主要な技術・手法* 
## *有効性の検証方法* 
## *議論および課題* 
"""

# Slack channel
POST_CHANNEL = [
    os.environ.get(key) for key in os.environ.keys() if "POST_CHANNEL" in key
]

# RSS publisher
PUBLISH = dict(ArXiv="cs.CV", MDPI="remotesensing")

# Slack color list
COLOR = ["#d7003a", "#f6ad49", "#ffdb4f", "#00a381", "#89c3eb", "#bbc8e6", "#a59aca"]
