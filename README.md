# arxiv-satellite

## 概要

リモセン関連の論文を取得するSlackbotです.  
検索先はarXiv CS-CVとMDPI Remote Sensingに対応しています.  
keywordや検索先を変えることで他のジャンルの論文も検索することが出来ます.  
DeepLによる翻訳結果も一緒に表示されます（DeepLが制限に引っかかる場合はMicrosoft Translatorを使用するようになっています）.

## 環境変数

* GitHub Actionsを使用する際は`ENVIRONMENTS`というSecretsに使用するすべての環境変数をセットしてください
* 必要な変数は以下になります.
    + SLACK_API_TOKEN: SlackbotのBot User OAuth Token. 複数workspaceで使用する場合はSLACK_API_TOKEN1という風に「SLACK_API_TOKEN」にsuffixをつけること
    + DEEPL_API_TOKEN: DeepLのAPIキー
    + MS_TRANSLATE_KEY: Microsoft TranslatorのKey1
    + MS_TRANSLATE_REGION: Microsoft Translatorのregion
    + POST_CHANNEL: 投稿先のチャンネル名. 複数workspaceで使用する場合はPOST_CHANNEL1という風に「POST_CHANNEL」にsuffixをつけること
* `slackbot_setting.py`内の`PUBLISH`には論文検索先をkeyに、ジャンルをvalueとしたdictionaryを作成してください.  
    + 論文検索先のジャンルが複数ある場合はvalueをlist型にして渡してください

## 検索キーワード

`keyword.yml`に記載してください

|属性key|説明|
|:--:|:--|
|fixed|表記をkeyword.ymlに記載のままで検索したい単語を入力
|variable|表記がブレやすい単語を入力
