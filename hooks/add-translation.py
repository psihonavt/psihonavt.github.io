import configparser
import re
from datetime import date, datetime
from pathlib import Path

import mkdocs
from magentic import prompt
from magentic.chat_model.openai_chat_model import OpenaiChatModel
from magentic.chat_model.anthropic_chat_model import AnthropicChatModel
from pydantic import BaseModel


config = configparser.ConfigParser()
config.read("config.ini")

OPENAI_API_KEY = config["main"]["OPENAI_API_KEY"]
openai_model = OpenaiChatModel("gpt-4o", api_key=OPENAI_API_KEY)

ANTHROPIC_API_KEY = config["main"]["ANTHROPIC_API_KEY"]
anthropic_model = AnthropicChatModel(
    "claude-3-5-sonnet-latest", api_key=ANTHROPIC_API_KEY, max_tokens=8192
)

TRANSLATE_ENTRY_PROMPT = """You're my assistant who translates entries from journal from English to Ukrainian. Your task is to produce
an accurate Ukrainian version while maintaining style, humor, "mood" of an original entry. That is, no need to translate text word to word – rather keep
the style and mood. Also keep all markdown tags and special symbols as it is. Always translate "Miles driven" as "КМ проїхав". Convert miles to kilometers.
English entry is {entry}"""

URIS_TO_TRANSLATE = ["roadtrip1", "pub"]


class JournalEntry(BaseModel):
    date: date | None
    subtitle: str | None
    content: str

    def heading(self, suffix=""):
        if self.date:
            return f"{self.date.strftime('%m/%d/%Y')}{suffix}\n--\n"
        else:
            return f"{self.subtitle}{suffix}\n--\n"

    @property
    def clean_subtitle(self) -> None | str:
        return self.subtitle and self.subtitle.strip("\n")


class Document(BaseModel):
    non_entries: str
    entries: list[JournalEntry]
    title: str


class TranslatedEntry(BaseModel):
    content: str


def _translate_entry(model, entry: JournalEntry, title: str) -> str:
    @prompt(TRANSLATE_ENTRY_PROMPT, model=model, max_retries=5)
    def _fn(entry: str) -> TranslatedEntry: ...

    if entry.date:
        maybe_translation = Path(
            f"hooks/translations/{entry.date.strftime('%m-%d-%Y')}.ukr.{model.model}.txt"
        )
    else:
        maybe_translation = Path(
            f"hooks/translations/{title}.{entry.clean_subtitle}.ukr.{model.model}.txt"
        )
    if not maybe_translation.exists():
        print(f"{maybe_translation} not cached")
        translation = _fn(entry.content)
        with open(maybe_translation, "w") as f:
            f.write(translation.model_dump_json())
    else:
        print(f"{maybe_translation} cached")
        with open(maybe_translation, "r") as f:
            translation = TranslatedEntry.model_validate_json(f.read())

    return translation.content


def get_md_document(content: str, title: str) -> Document:
    date_pattern = r"(\d{2}/\d{2}/\d{4})\n--\n"
    subtitle_pattern = r"(.*?)\n--\n"

    first_header_match = re.search(date_pattern, content)
    is_date_format = bool(first_header_match)

    # Choose the appropriate pattern based on file type
    if is_date_format:
        pattern = date_pattern
    else:
        pattern = subtitle_pattern

    sections = re.split(pattern, content.strip())
    entries = []

    # Process pairs of (date, content)
    for i in range(1, len(sections) - 1, 2):
        entry_title, entry_date = None, None
        date_or_title_str = sections[i]
        text = sections[i + 1].strip()

        # Parse the date string
        if is_date_format:
            entry_date = datetime.strptime(date_or_title_str, "%m/%d/%Y").date()
        else:
            entry_title = date_or_title_str

        # Create RawEntry object
        entry = JournalEntry(date=entry_date, content=text, subtitle=entry_title)
        entries.append(entry)

    # Sort entries by date
    entries.sort(key=lambda x: x.date or 0)
    return Document(non_entries=sections[0], entries=entries, title=title)


def add_translation(document: Document) -> str:
    resulting_md = document.non_entries + "\n\n[EN]\n\n"
    for entry in document.entries:
        resulting_md += entry.heading()
        resulting_md += entry.content + "\n\n"

    resulting_md += "\n\n[UKR]\n\n"

    for entry in document.entries:
        resulting_md += entry.heading("[UKR]")
        resulting_md += (
            _translate_entry(anthropic_model, entry, document.title) + "\n\n"
        )

    return resulting_md


@mkdocs.plugins.event_priority(-1)
def on_page_markdown(markdown, **kwargs):
    if any(uri in kwargs["page"].url for uri in URIS_TO_TRANSLATE):
        document = get_md_document(markdown, kwargs["page"].title)
        return add_translation(document)
    return markdown
