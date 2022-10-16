# arxiv-satellite

## 概要

CS-CVにあるリモセン関連の論文を取得するSlackbotです.  
keywordや検索先を変えることで他のジャンルの論文も検索することが出来ます.  
DeepLによる翻訳結果も一緒に表示されます.

## 環境変数

* `DEEPL_API_TOKEN`と`SLACK_API_TOKEN`にそれぞれDeepLのAPIキーとIncoming WebHookのAPIキーをセットしてください
* `slackbot_setting.py`内の`CHANNEL`にはslackのworkspace内のチャンネル名を指定してください

## 検索キーワード

`keyword.yml`に記載してください
