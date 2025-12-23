import re
import uuid
from time import perf_counter, sleep

import requests
from deepl import Translator, exceptions
from google import genai
from google.genai.types import GenerateContentConfig

import slackbot_settings


class ArticleTranslator:
    def __call__(self, description: str) -> dict[str, str | dict[str, str | bool]]:
        """
        Translate the description of an article.

        Args:
            description (str): The description to translate.

        Returns:
            (dict[str, str | dict[str, str | bool]]): A dictionary containing the original and translated descriptions.
        """
        try:
            translate_description = self.deepl_translator(description)
        except exceptions.DeepLException:
            translate_description = self.microsoft_translator(description)
        except Exception:
            translate_description = description
        finally:
            return translate_description

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
        return translator.translate_text(
            description, source_lang="EN", target_lang="JA"
        ).text

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


class ArticleSummarizer:
    def __call__(self, link: str) -> dict:
        """
        Summarize an article.

        Args:
            link (str): The link to the article.

        Returns:
            (dict): A dictionary containing the summary of the article.
        """
        try:
            summary = self.gemini_summarize(link)
            summary = (
                self.extract_after_last(summary) if summary is not None else summary
            )
        except Exception:
            summary = None
        finally:
            # return self.format_summarize_for_attachment(summary)
            return self.format_summarize_for_blocks(summary)

    @staticmethod
    def gemini_summarize(url: str) -> str | None:
        """
        Summarize an article using Gemini API.

        Args:
            url (str): The URL of the article to summarize.

        Returns:
            (str | None): The summary of the article.
        """
        client = genai.Client(api_key=slackbot_settings.GEMINI_API_TOKEN)
        contents = f"{slackbot_settings.PROMPT}{url}"
        config = GenerateContentConfig(
            tools=[
                {"url_context": {}},
                # {"google_search": {}},
            ],
            temperature=0.0,
        )

        try:
            start = perf_counter()
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=contents,
                config=config,
            )
            elapsed = perf_counter() - start
            sleep(max(int(12 - elapsed), 0) + 1)  # for gemini rate limit
            output = response.text
        except genai.errors.APIError as e:
            match getattr(e, "code", None):
                case 429:
                    start = perf_counter()
                    response = client.models.generate_content(
                        model="gemini-2.5-flash-lite",
                        contents=contents,
                        config=config,
                    )
                    elapsed = perf_counter() - start
                    sleep(max(int(6 - elapsed), 0) + 1)  # for gemini rate limit
                    output = response.text
                case _:
                    output = None

        return output

    @staticmethod
    def extract_after_last(text: str, marker: str = "*研究の概要*") -> str | None:
        """
        Extracts the substring after the last occurrence of a specified marker in the text.

        Args:
            text (str): The input text to search within.
            marker (str, optional): The marker string to search for. Defaults to "*研究の概要*".

        Returns:
            (str | None): The substring from the last occurrence of the marker to the end of the text, or None if the marker is not found.
        """
        idx = text.rfind(marker)
        if idx == -1:
            return None
        return text[idx:]

    @staticmethod
    def format_summarize_for_attachment(summary: str) -> list[dict[str, str | bool]]:
        """
        Format a summary text for Slack attachment fields by parsing Markdown sections and improving list formatting.

        Args:
            summary (str): The raw summary text in Markdown format containing sections with ## headings. May contain various line ending formats (\r\n, \r, \n).

        Returns:
            (list[dict[str, str | bool]]): A list of dictionaries representing Slack attachment fields.
        """
        # Important: Use \Z instead of $ for string end matching (works correctly with MULTILINE flag)
        pattern = re.compile(
            r"^##\s+([^\n]+)\n(.*?)(?=\n##\s+|\Z)",
            flags=re.MULTILINE | re.DOTALL,
        )

        fields = []
        for title, body in pattern.findall(
            summary.replace("\r\n", "\n").replace("\r", "\n").strip()
        ):
            title = title.strip()
            value = re.sub(
                r"([^\n])\n(\d+\.)", r"\1\n\n\2", body.strip()
            )  # ordered list
            value = re.sub(r"([^\n])\n([-*]\s)", r"\1\n\n\2", value)  # unordered list
            if not title or not value:
                continue

            fields.append({"title": title, "value": value, "short": False})
        return fields

    @staticmethod
    def format_summarize_for_blocks(summary: str | None) -> str:
        """
        Format a summary text for Slack block rendering by converting Markdown-style formatting to Slack-compatible formatting.

        Args:
            summary (str | None): The raw summary text containing Markdown-style formatting. May contain various line ending formats (\r\n, \r, \n).

        Returns:
            (str): The formatted summary text with Slack-compatible formatting. Headings and bold text are converted to use Slack's *text* syntax.
        """
        if summary is None:
            return ""

        # Normalize line endings to Unix-style (\n)
        s = summary.replace("\r\n", "\n").replace("\r", "\n").strip()

        # Converts Markdown bold syntax (**text** or __text__) to Slack bold format (*text*)
        s = re.sub(r"\*\*(.+?)\*\*", r"*\1*", s)
        s = re.sub(r"__(.+?)__", r"*\1*", s)

        return s
