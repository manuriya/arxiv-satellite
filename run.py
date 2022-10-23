# coding: UTF-8
import re
from datetime import datetime, timezone
from typing import Union

import feedparser
from deepl import Translator
from omegaconf import OmegaConf
from slack_sdk import WebClient

import slackbot_settings


def format_article(article: feedparser.util.FeedParserDict, color: str) -> dict[str, str]:
    title = re.sub(r" .(arXiv:.*)", "", article.title)  # Extract only paper's title
    link = article.link.replace("http", "https")
    description = " ".join(article.description[3:].replace("\n", "").split("</p>")[0].split(" "))
    authors = ", ".join(
        [re.sub(r"<a href=.*\">", "", author).replace("</a>", "") for author in article.author.split(",")])
    translator = Translator(slackbot_settings.DEEPL_API_TOKEN)
    translate_description = translator.translate_text(description, source_lang="EN", target_lang="JA").text
    fields = [
        dict(title="English", value=description, short=True),
        dict(title="Japanese", value=translate_description, short=True)
    ]
    return dict(title=title, title_link=link, author=authors, fields=fields, color=color)


def match_paper(rss: feedparser.util.FeedParserDict, patterns: re.Pattern) -> dict[str, str]:
    # Check RSS updated date
    updated_date = datetime(*rss.updated_parsed[:6], tzinfo=timezone.utc).date()
    if updated_date < datetime.now(timezone.utc).date():
        yield None
    else:
        # Search for articles containing keys
        count = 0
        for article in rss.entries:
            if bool([p.search(article.title) for p in patterns if p.search(article.title) is not None]):
                count += 1
                yield format_article(article, slackbot_settings.COLOR[(count - 1) % 7])


def format_header(article: dict[str, Union[str, dict[str, str]]]) -> str:
    title = f"*{article['title']}*\n"
    link = f"{article['title_link']}\n"
    author = f"{article['author']}\n"
    return title + link + author


def main(patterns: list[re.Pattern]) -> None:
    # Get matching papers
    rss = feedparser.parse(slackbot_settings.CSCV)
    articles = [i for i in list(match_paper(rss, patterns)) if i is not None]

    # Post message to slack channel
    slack = WebClient(slackbot_settings.SLACK_API_TOKEN)
    for article in articles:
        text = format_header(article)
        attachment = dict(title="Abstract", fields=article["fields"], color=article["color"])
        slack.chat_postMessage(channel=slackbot_settings.CHANNEL,
                               text=text,
                               as_user=True,
                               unfurl_links=False,
                               attachments=[attachment])


if __name__ == "__main__":
    keywords = OmegaConf.load("keyword.yml")
    main([re.compile(p, re.IGNORECASE) for p in sum([keywords[key] for key in keywords], [])])
