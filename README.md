# arxiv-satellite

## 概要

リモセン関連の論文を取得するSlackbotです.  
検索先はarXiv CS-CVとMDPI Remote Sensingに対応しています.  
keywordや検索先を変えることで他のジャンルの論文も検索することが出来ます.  
DeepLによる翻訳結果も一緒に表示されます.

## 環境変数

* `DEEPL_API_TOKEN`と`SLACK_API_TOKEN`にそれぞれDeepLのAPIキーとIncoming WebHookのAPIキーをセットしてください
* `slackbot_setting.py`内の`CHANNEL`にはslackのworkspace内のチャンネル名を指定してください
* `slackbot_setting.py`内の`PUBLISH`には論文検索先をkeyに、ジャンルをvalueとしたdictionaryを作成してください.  
    + 論文検索先のジャンルが複数ある場合はvalueをlist型にして渡してください

## 検索キーワード

`keyword.yml`に記載してください
