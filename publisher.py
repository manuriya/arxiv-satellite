import re
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone

import feedparser
from deepl import Translator
from feedparser.util import FeedParserDict

import slackbot_settings


class Publisher(ABC):

    @abstractmethod
    def get_publish_date(self, article: FeedParserDict) -> datetime:
        pass

    @staticmethod
    @abstractmethod
    def parse_title(title: str) -> str:
        pass

    @abstractmethod
    def format_article(self, article: FeedParserDict, color: str) -> dict[str, str]:
        pass

    def get_articles(self, patterns: list[re.Pattern]) -> dict[str, str]:
        count = 0
        for article in self.rss.entries:
            updated_date = self.get_publish_date(article)
            if updated_date < datetime.now(timezone.utc).date():
                yield None
            else:
                title = self.parse_title(article.title)
                if bool([p.search(title) for p in patterns if p.search(title) is not None]):
                    count += 1
                    yield self.format_article(article, slackbot_settings.COLOR[(count - 1) % 7])

    @staticmethod
    def translate(description: str) -> list[dict]:
        translator = Translator(slackbot_settings.DEEPL_API_TOKEN)
        translate_description = translator.translate_text(description, source_lang="EN", target_lang="JA").text
        return [
            dict(title="English", value=description, short=True),
            dict(title="Japanese", value=translate_description, short=True)
        ]


class ArXiv(Publisher):

    def __init__(self, genre: str) -> None:
        self.rss = feedparser.parse(f"https://export.arxiv.org/rss/{genre}")

    def get_publish_date(self, article: FeedParserDict) -> datetime:
        return datetime(*self.rss.updated_parsed[:6], tzinfo=timezone.utc).date()

    @staticmethod
    def parse_title(title: str) -> str:
        return re.sub(r" .(arXiv:.*)", "", title)

    def format_article(self, article: FeedParserDict, color: str) -> dict[str, str]:
        title = self.parse_title(article.title)
        link = article.link.replace("http", "https")
        description = " ".join(article.description[3:].replace("\n", "").split("</p>")[0].split(" "))
        authors = ", ".join(
            [re.sub(r"<a href=.*\">", "", author).replace("</a>", "") for author in article.author.split(",")])

        return dict(title=title, title_link=link, author=authors, fields=self.translate(description), color=color)


class MDPI(Publisher):

    def __init__(self, genre: str) -> None:
        self.rss = feedparser.parse(f"https://www.mdpi.com/rss/journal/{genre}")

    def get_publish_date(self, article: FeedParserDict) -> datetime:
        return datetime(*article.published_parsed[:6], tzinfo=timezone.utc).date() + timedelta(days=1)

    @staticmethod
    def parse_title(title: str) -> str:
        return re.sub(r".*[0-9]: ", "", title)

    def format_article(self, article: FeedParserDict, color: str) -> dict[str, str]:
        title = self.parse_title(article.title)
        link = article.link
        description = " ".join(article.summary.replace("\'", "").split(" "))
        authors = ", ".join([author["name"] for author in article.authors])
        return dict(title=title, title_link=link, author=authors, fields=self.translate(description), color=color)
