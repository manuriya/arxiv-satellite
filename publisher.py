import re
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from typing import Generator

import feedparser
import requests
from deepl import Translator, exceptions
from feedparser.util import FeedParserDict

import slackbot_settings


class Publisher(ABC):
    """
    Abstract base class for a publisher that retrieves and formats articles.
    """

    @abstractmethod
    def get_publish_date(self, article: FeedParserDict) -> datetime:
        """
        Get the publish date of an article.

        Args:
            article (FeedParserDict): The article to get the publish date for.

        Returns:
            (datetime): The publish date of the article.
        """
        pass

    @staticmethod
    @abstractmethod
    def parse_title(title: str) -> str:
        """
        Parse the title of an article.

        Args:
            title (str): The title of the article.

        Returns:
            (str): The parsed title.
        """
        pass

    @abstractmethod
    def format_article(self, article: FeedParserDict, color: str) -> dict[str, str]:
        """
        Format an article for display.

        Args:
            article (FeedParserDict): The article to format.
            color (str): The color to use for the article.

        Returns:
            (dict[str, str]): The formatted article.
        """
        pass

    def get_articles(self, patterns: list[re.Pattern]) -> Generator[dict[str, str] | None, None, None]:
        """
        Retrieve articles that match the given patterns.

        Args:
            patterns (list[re.Pattern]): A list of compiled regex patterns.

        Yields:
            (Generator[dict[str, str] | None, None, None]): A generator of formatted articles or None.
        """
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

    def translate(self, description: str) -> list[dict]:
        """
        Translate the description of an article.

        Args:
            description (str): The description to translate.

        Returns:
            (list[dict]): A list of dictionaries containing the original and translated descriptions.
        """
        try:
            translate_description = self.deepl_translator(description)
        except exceptions.DeepLException:
            translate_description = self.microsoft_translator(description)
        except Exception:
            translate_description = description
        finally:
            return [
                dict(title="English", value=description, short=True),
                dict(title="Japanese", value=translate_description, short=True),
            ]

    @staticmethod
    def deepl_translator(description: str) -> str:
        """
        Translate a description using DeepL.

        Args:
            description (str): The description to translate.

        Returns:
            (str): The translated description.
        """
        translator = Translator(slackbot_settings.DEEPL_API_TOKEN)
        return translator.translate_text(description, source_lang="EN", target_lang="JA").text

    @staticmethod
    def microsoft_translator(description: str) -> str:
        """
        Translate a description using Microsoft Translator.

        Args:
            description (str): The description to translate.

        Returns:
            (str): The translated description.
        """
        url = "https://api.cognitive.microsofttranslator.com/translate?api-version=3.0&from=en&to=ja"
        headers = {
            "Ocp-Apim-Subscription-Key": slackbot_settings.MS_TRANSLATE_KEY,
            "Ocp-Apim-Subscription-Region": slackbot_settings.MS_TRANSLATE_REGION,
            "Content-type": "application/json",
            "X-ClientTraceId": str(uuid.uuid4()),
        }
        request = requests.post(url, headers=headers, json=[dict(text=description)])
        response = request.json()
        return response[0]["translations"][0]["text"]


class ArXiv(Publisher):
    """
    A publisher class for retrieving and formatting articles from the ArXiv RSS feed.
    """

    def __init__(self, genre: str) -> None:
        """
        Initialize the ArXiv publisher with a specific genre.

        Args:
            genre (str): The genre of articles to retrieve.
        """
        self.rss = feedparser.parse(f"https://rss.arxiv.org/rss/{genre}")

    def get_publish_date(self, article: FeedParserDict) -> datetime:
        """
        Get the publish date of an article.

        Args:
            article (FeedParserDict): The article to get the publish date for.

        Returns:
            (datetime): The publish date of the article.
        """
        return datetime(*self.rss.feed.updated_parsed[:6], tzinfo=timezone.utc).date()

    @staticmethod
    def parse_title(title: str) -> str:
        """
        Parse the title of an article.

        Args:
            title (str): The title of the article.

        Returns:
            (str): The parsed title.
        """
        return re.sub(r" .(arXiv:.*)", "", title)

    def format_article(self, article: FeedParserDict, color: str) -> dict[str, str]:
        """
        Format an article for display.

        Args:
            article (FeedParserDict): The article to format.
            color (str): The color to use for the article.

        Returns:
            (dict[str, str]): The formatted article.
        """
        title = self.parse_title(article.title)
        link = article.link.replace("http:", "https:")
        description = " ".join(article.description.split("Abstract:")[1].replace("\n", "").split("</p>")[0].split(" "))
        authors = ", ".join(
            [re.sub(r"<a href=.*\">", "", author).replace("</a>", "") for author in article.author.split(",")]
        )
        return dict(
            title=title,
            title_link=link,
            author=authors,
            fields=self.translate(description),
            color=color,
        )


class MDPI(Publisher):
    """
    A publisher class for retrieving and formatting articles from the MDPI RSS feed.
    """

    def __init__(self, genre: str) -> None:
        """
        Initialize the MDPI publisher with a specific genre.

        Args:
            genre (str): The genre of articles to retrieve.
        """
        self.rss = feedparser.parse(f"https://www.mdpi.com/rss/journal/{genre}")

    def get_publish_date(self, article: FeedParserDict) -> datetime:
        """
        Get the publish date of an article.

        Args:
            article (FeedParserDict): The article to get the publish date for.

        Returns:
            (datetime): The publish date of the article.
        """
        return datetime(*article.published_parsed[:6], tzinfo=timezone.utc).date() + timedelta(days=1)

    @staticmethod
    def parse_title(title: str) -> str:
        """
        Parse the title of an article.

        Args:
            title (str): The title of the article.

        Returns:
            (str): The parsed title.
        """
        return re.sub(r".*[0-9]: ", "", title)

    def format_article(self, article: FeedParserDict, color: str) -> dict[str, str]:
        """
        Format an article for display.

        Args:
            article (FeedParserDict): The article to format.
            color (str): The color to use for the article.

        Returns:
            (dict[str, str]): The formatted article.
        """
        title = self.parse_title(article.title)
        link = article.link
        description = " ".join(article.summary.replace("'", "").split(" "))
        authors = ", ".join([author["name"] for author in article.authors])
        return dict(
            title=title,
            title_link=link,
            author=authors,
            fields=self.translate(description),
            color=color,
        )
