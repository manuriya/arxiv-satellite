# coding: UTF-8
import re
from formatter import BlockCreator
from importlib import import_module

from omegaconf import OmegaConf
from slack_sdk import WebClient

import slackbot_settings


def create_patterns(yaml_name: str) -> list[re.Pattern]:
    """
    Create a list of regex patterns from a YAML file.

    Args:
        yaml_name (str): The name of the YAML file containing keywords.

    Returns:
        (list[re.Pattern]): A list of compiled regex patterns.
    """
    keywords = OmegaConf.load(yaml_name)
    patterns = []
    for key in keywords:
        match key:
            case "fixed":
                patterns.extend([re.compile(p) for p in keywords[key]])
            case "variable":
                for p in keywords[key]:
                    patterns.append(re.compile(p, re.IGNORECASE))
                    if len(p.split(" ")) > 1:
                        patterns.append(
                            re.compile("".join(p.split(" ")), re.IGNORECASE)
                        )
            case _:
                raise ValueError(f"Invalid keyword: {key}")
    return patterns


def get_articles(patterns: list[re.Pattern]) -> list[dict[str, str]]:
    """
    Retrieve articles that match the given patterns.

    Args:
        patterns (list[re.Pattern]): A list of compiled regex patterns.

    Returns:
        (list[dict[str, str]]): A list of dictionaries containing article information.
    """
    articles = []
    for publish, genre in slackbot_settings.PUBLISH.items():
        genre = [genre] if isinstance(genre, str) else genre
        for g in genre:
            target = getattr(import_module("publisher"), publish)(genre=g)
            articles.extend(
                [i for i in list(target.get_articles(patterns)) if i is not None]
            )
    return articles


def main(patterns: list[re.Pattern]) -> None:
    """
    Main function to post articles to Slack channels.

    Args:
        patterns (list[re.Pattern]): A list of compiled regex patterns.
    """
    slacks = [WebClient(token) for token in slackbot_settings.SLACK_API_TOKEN]
    for article in get_articles(patterns):
        if len(article["description"]) == 0 or len(article["description"]) > 3000:
            continue
        try:
            for slack, channel in zip(slacks, slackbot_settings.POST_CHANNEL):
                slack.chat_postMessage(
                    channel=channel,
                    text="",
                    as_user=True,
                    unfurl_links=False,
                    blocks=BlockCreator()(article),
                )
        except Exception as e:
            print(article)
            print(f"Error posting to Slack: {e}")


if __name__ == "__main__":
    main(create_patterns("keyword.yml"))
