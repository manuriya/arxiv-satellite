# coding: UTF-8
import re
from importlib import import_module

from omegaconf import OmegaConf
from slack_sdk import WebClient

import slackbot_settings


def get_articles(patterns: list[re.Pattern]) -> list[dict[str, str]]:
    articles = []
    for publish, genre in slackbot_settings.PUBLISH.items():
        genre = [genre] if isinstance(genre, str) else genre
        for g in genre:
            target = getattr(import_module("publisher"), publish)(genre=g)
            articles.extend([i for i in list(target.get_articles(patterns)) if i is not None])
    return articles


def main(patterns: list[re.Pattern]) -> None:
    articles = get_articles(patterns)
    slacks = [WebClient(token) for token in slackbot_settings.SLACK_API_TOKEN]

    # Post message to slack channel
    for article in articles:
        text = f"*{article['title']}*\n" + f"{article['title_link']}\n" + f"{article['author']}\n"
        attachment = dict(title="Abstract", fields=article["fields"], color=article["color"])

        for slack in slacks:
            slack.chat_postMessage(
                channel=slackbot_settings.CHANNEL,
                text=text,
                as_user=True,
                unfurl_links=False,
                attachments=[attachment],
            )


if __name__ == "__main__":
    keywords = OmegaConf.load("keyword.yml")
    main([re.compile(p, re.IGNORECASE) for p in sum([keywords[key] for key in keywords], [])])
