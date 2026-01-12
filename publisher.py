import re
from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta, timezone
from typing import Generator

import feedparser
import requests
from feedparser.util import FeedParserDict

from function import ArticleSummarizer, ArticleTranslator


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

    def format_article(
        self, article: FeedParserDict, patterns: list[re.Pattern]
    ) -> dict[str, str]:
        """
        Format an article for display.

        Args:
            article (FeedParserDict): The article to format.
            patterns (list[re.Pattern]): A list of compiled regex patterns.

        Returns:
            (dict[str, str]): The formatted article.
        """

        title, link, authors, description = self.extract_keyword(article)
        description = ArticleSummarizer()(link, patterns)
        match len(description):
            case 0:
                description = ArticleTranslator()(description)
            case _:
                description = description

        return dict(
            title=title,
            title_link=link,
            author=authors,
            description=description,
        )

    @abstractmethod
    def extract_keyword(self, article: FeedParserDict) -> tuple[str, str, str, str]:
        """
        Extract keywords from an article.

        Args:
            article (FeedParserDict): The article to extract keywords from.

        Returns:
            (tuple[str, str, str, str]): A tuple containing the title, link, authors, and description.
        """
        pass

    def get_articles(
        self, patterns: list[re.Pattern]
    ) -> Generator[dict[str, str] | None, None, None]:
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
                if bool(
                    [p.search(title) for p in patterns if p.search(title) is not None]
                ):
                    count += 1
                    print(f"Progress: {count:02}")
                    yield self.format_article(article, patterns)


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

    def extract_keyword(self, article: FeedParserDict) -> dict[str, str]:
        """
        Extract keywords from an article.

        Args:
            article (FeedParserDict): The article to extract keywords from.

        Returns:
            (tuple[str, str, str, str]): A tuple containing the title, link, authors, and description.
        """
        title = self.parse_title(article.title)
        link = article.link.replace("http:", "https:")
        description = " ".join(
            article.description.split("Abstract:")[1]
            .replace("\n", "")
            .split("</p>")[0]
            .split(" ")
        )
        authors = ", ".join(
            [
                re.sub(r"<a href=.*\">", "", author).replace("</a>", "")
                for author in article.author.split(",")
            ]
        )
        return title, link, authors, description


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
        # self.rss = OpenAlex(issn="2072-4292").rss

    def get_publish_date(self, article: FeedParserDict) -> datetime:
        """
        Get the publish date of an article.

        Args:
            article (FeedParserDict): The article to get the publish date for.

        Returns:
            (datetime): The publish date of the article.
        """
        return datetime(
            *article.published_parsed[:6], tzinfo=timezone.utc
        ).date() + timedelta(days=1)

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

    def extract_keyword(self, article: FeedParserDict) -> tuple[str, str, str, str]:
        """
        Extract keywords from an article.

        Args:
            article (FeedParserDict): The article to extract keywords from.

        Returns:
            (tuple[str, str, str, str]): A tuple containing the title, link, authors, and description.
        """
        title = self.parse_title(article.title)
        link = article.link
        description = " ".join(article.summary.replace("'", "").split(" "))
        authors = ", ".join([author["name"] for author in article.authors])
        return title, link, authors, description


class OpenAlex(Publisher):
    """
    A publisher class for retrieving and formatting articles from OpenAlex API.
    """

    def __init__(self, issn: str) -> None:
        self.rss = self.fetch_openalex_new_works(issn=issn)

    @staticmethod
    def fetch_openalex_new_works(issn, days_back=2, per_page=200) -> dict:
        """
        Fetch recently published works from OpenAlex API for a given journal ISSN.

        Args:
            issn (str): The ISSN (International Standard Serial Number) of the journal to query.
            days_back (int, optional): Number of days to look back from today for new publications.
            per_page (int, optional): Maximum number of results to retrieve per page.

        Returns:
            _type_: _description_

        Raises:
            requests.exceptions.HTTPError: If the API request fails.
            requests.exceptions.Timeout: If the request times out after 30 seconds.
        """
        from_date = (date.today() - timedelta(days=days_back)).isoformat()
        params = {
            "filter": f"primary_location.source.issn:{issn},from_publication_date:{from_date}",
            "sort": "publication_date:desc",
            "per-page": per_page,
            "select": "doi,title,publication_date,primary_location,abstract_inverted_index",
        }
        r = requests.Session().get(
            "https://api.openalex.org/works", params=params, timeout=30
        )
        r.raise_for_status()
        return r.json().get("results", [])

    @staticmethod
    def abstract_to_text(inv):
        if not inv:
            return None
        # inv: {word: [pos1,pos2,...], ...}
        pos_to_word = {}
        for word, positions in inv.items():
            for p in positions:
                pos_to_word[p] = word
        if not pos_to_word:
            return None
        words = [pos_to_word[p] for p in sorted(pos_to_word)]
        return " ".join(words)

    def get_publish_date(self, article: FeedParserDict) -> datetime:
        """
        Get the publish date of an article.

        Args:
            article (FeedParserDict): The article to get the publish date for.

        Returns:
            (datetime): The publish date of the article.
        """
        return datetime(
            *article.published_parsed[:6], tzinfo=timezone.utc
        ).date() + timedelta(days=1)

    def extract_keyword(self, article: FeedParserDict) -> tuple[str, str, str, str]:
        """
        Extract keywords from an article.

        Args:
            article (FeedParserDict): The article to extract keywords from.

        Returns:
            (tuple[str, str, str, str]): A tuple containing the title, link, authors, and description.
        """
        title = self.parse_title(article.title)
        link = article.link
        description = " ".join(article.summary.replace("'", "").split(" "))
        authors = ", ".join([author["name"] for author in article.authors])
        return title, link, authors, description

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
