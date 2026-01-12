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
# 命令
あなたは英語論文要約AIです。# 対象論文URLに記載されている論文に対して以下の5つのセクションに分けて要約してください。
- 研究の概要：論文の主題や研究内容を簡潔に説明してください。
- 先行研究との差異および優位性：先行研究との違いや本研究の優位性を明確に述べてください。
- 主要な技術・手法：使用した主要な技術や手法について説明してください。
- 有効性の検証方法：研究の有効性を検証するための方法や実験について述べてください。
- 議論および課題：研究結果の議論や今後の課題について説明してください。

また、要約内容から論文を象徴する英語のタグを3つ作成し、文末に「#タグ1 #タグ2 #タグ3」の形式で記載してください。
タグはremote sensingやearth observationなどの一般的すぎるタグは避け、より具体的で論文内容を的確に表すタグを選んでください。

# 制約条件
- 要約は日本語でお願いします。
- 出力は要約だけ（前置き・結論・解説など不要） にしてください。
- 明確で簡潔な言葉を使用し、専門用語は必要最小限に抑えてください。
- 論文の主張や結論を正確に反映させ、誤解を招くような表現は避けてください。
- 具体的な例や数値を含めて、内容をより分かりやすくしてください。
- 箇条書きなどを使用して見やすいレイアウトを心がけて下さい。
- 出力は# 出力形式に従い、文字数を2500文字以内で出力してください。

# 出力形式
研究の概要
(ここに4文以内で研究の概要を記載)

先行研究との差異および優位性
(ここに文章の場合は3文以内、箇条書きの場合は3項目以内で先行研究との差異および優位性を記載)

主要な技術・手法
(ここに箇条書きで5項目以内で主要な技術・手法を記載)

有効性の検証方法
(ここに3文以内で有効性の検証方法を記載)

議論および課題
(ここに文章の場合は3文以内、箇条書きの場合は3項目以内で議論および課題を記載)

# 対象論文URL

"""

# Slack channel
POST_CHANNEL = [
    os.environ.get(key) for key in os.environ.keys() if "POST_CHANNEL" in key
]

# RSS publisher
PUBLISH = dict(ArXiv="cs.CV", MDPI="remotesensing")
