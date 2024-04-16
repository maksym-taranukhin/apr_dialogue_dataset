import logging
import os
from pathlib import Path
from urllib.parse import urlparse
from unstructured.documents.html import HTMLListItem, HTMLNarrativeText, HTMLTitle
from unstructured.partition.text_type import sentence_count

import pandas as pd

def save_docs_as_md(df: pd.DataFrame, path: Path) -> None:
    """
    Save each document to a separate file with the name of the source.
    """

    def save_doc(row):
        _path = path / urlparse(row["source"]).path.lstrip("/").replace("/", "_")
        if not _path.exists():
            _path.mkdir(parents=True)

        filename = row.name

        with open(_path / f"{filename}.md", "w") as f:
            metadata_str = "\n\n".join([f"{k}: {v}" for k, v in row.items() if k != "text"])
            _str = f"{metadata_str}\n\n{row['text']}"
            f.write(_str)
            logging.info(f"Saved {_path / f'{filename}.md'}")

    df.apply(save_doc, axis=1)

    logging.info(f"Saved {len(df)} markdown documents to {path}")


def save_docs_as_json(df: pd.DataFrame, path: Path) -> None:
    """
    Save each document to a separate file with the name of the source.
    """

    def save_doc(row):
        _path = path / urlparse(row["source"]).path.lstrip("/").replace("/", "_")
        if not _path.exists():
            _path.mkdir(parents=True)

        filename = row.name

        with open(_path / f"{filename}.json", "w") as f:
            row.to_json(f, indent=4)
            logging.info(f"Saved {_path / f'{filename}.json'}")

    df.apply(save_doc, axis=1)

    logging.info(f"Saved {len(df)} json documents to {path}")


def format_parsed_html_as_md(parsed_html: list) -> str:
    """
    Format parsed html as markdown.
    """
    text = ""
    for e in parsed_html:
        sep = "\n\n"
        if isinstance(e, HTMLListItem):
            sep = "\n" + " " * (e.metadata.category_depth - 1) + "- "
        if isinstance(e, HTMLNarrativeText):
            sep = "\n"
            if sentence_count(e.text) <= 2 and e.text.endswith("?"):
                sep = "\n\n"
        if isinstance(e, HTMLTitle):
            sep = "\n\n" + "#" * (e.metadata.category_depth + 1) + " "
        text += f"{sep}{e.text}"
    return text.strip()
