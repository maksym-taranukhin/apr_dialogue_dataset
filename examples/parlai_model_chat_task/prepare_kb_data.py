import sys
import logging
import os
import re
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd
from dotenv import load_dotenv
from langchain_community.document_loaders.recursive_url_loader import (
    RecursiveUrlLoader,  # noqa
)
from unstructured.documents.html import HTMLListItem, HTMLNarrativeText, HTMLTitle
from unstructured.partition.html import partition_html
from unstructured.partition.text_type import sentence_count

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

DATA_DIR = Path(os.getenv("DATA_DIR", "data"))

def format_parsed_html_as_md(parsed_html: list) -> str:
    """
    Format the parsed html as markdown.
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


def lc_html_split(text):
    from langchain_text_splitters import HTMLHeaderTextSplitter
    headers_to_split_on = [
        ("h1", "Header 1"),
        ("h2", "Header 2"),
        ("h3", "Header 3"),
    ]

    html_splitter = HTMLHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    return [
        d
        for d in html_splitter.split_text(text)
        if d.metadata and "Header 1" in d.metadata
    ]


def lc_markdown_split(text):
    from langchain_text_splitters import MarkdownHeaderTextSplitter

    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]

    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    return markdown_splitter.split_text(text)
    # return [
    #     d
    #     for d in markdown_splitter.split_text(text)
    #     if d.metadata
    # ]

def scrape_airpassengerrights_ca() -> pd.DataFrame:
    """
    Scrape the airpassengerrights.ca website for practical guides.
    """
    URL = "https://airpassengerrights.ca/en/practical-guides/"
    # URL = "https://airpassengerrights.ca/en/practical-guides/denied-boarding/canada-pre-appr/glossary/glossary-of-terms"
    # URL = "https://airpassengerrights.ca/en/practical-guides/denied-boarding/european-union-and-economic-area/step-by-step-guide"

    # exclude the following pages
    EXCLUDE_URLS = [
        "https://airpassengerrights.ca/en/practical-guides/",
        "https://airpassengerrights.ca/en/practical-guides/denied-boarding/canada-pre-appr/faq",
        "https://airpassengerrights.ca/en/practical-guides/denied-boarding/canada-pre-appr",
    ]

    loader = RecursiveUrlLoader(URL, max_depth=99999, use_async=False, timeout=99)

    # extract the content from the pages starting from the first title
    docs_list = []
    for doc in loader.lazy_load():
        if doc.metadata['source'] in EXCLUDE_URLS:
            continue

        lc_docs = lc_html_split(doc.page_content)

        if len(lc_docs) > 1:
            docs_list.extend(
                [
                    {**doc.metadata, "text": lc_doc.page_content, **lc_doc.metadata}
                    for lc_doc in lc_docs
                ]
            )
            continue

        elements = partition_html(text=doc.page_content, skip_headers_and_footers=True)

        start_idx = 0
        for i, e in enumerate(elements):
            if isinstance(e, HTMLTitle):
                start_idx = i
                break

        end_idx = len(elements)
        for i, e in enumerate(reversed(elements)):
            if (
                isinstance(e, HTMLTitle)
                and e.text in ["Tweet", "Pin it", "Work in progress:"]
                or any(
                    e.text.startswith(prefix)
                    for prefix in [
                        "Step by Step Guide					",
                        "Step by Step Guide Follow ",
                        "FAQ Find answers",
                        "Glossary List of terms",
                    ]
                )
            ):
                end_idx = len(elements) - i - 1

        # fix merged enumerated items in titles by inserting a space
        pattern = r"(\s*\d+|\b\d+)([A-Za-z])|(\b[A-Za-z]+)([A-Z][a-z])"

        def replacement(match):
            if match.group(1):
                return match.group(1) + ' ' + match.group(2)
            return match.group(3) + ' ' + match.group(4)

        for e in elements[start_idx:end_idx]:
            if isinstance(e, HTMLTitle):
                e.text = re.sub(pattern, replacement, e.text)

        text = format_parsed_html_as_md(elements[start_idx:end_idx])

        lc_docs = lc_markdown_split(text)

        if len(lc_docs) >= 1:
            docs_list.extend(
                [
                    {**doc.metadata, "text": lc_doc.page_content, **lc_doc.metadata}
                    for lc_doc in lc_docs
                ]
            )
            continue

        print("Count not split the document: ", doc.metadata["source"])

    logging.info(f"Scraped {len(docs_list)} documents from airpassengerrights.ca")

    return pd.DataFrame(docs_list)


def scrape_rppa_appr_ca() -> pd.DataFrame:
    URL = "https://rppa-appr.ca/eng/"

    EXCLUDE_URLS = [
        "https://rppa-appr.ca/eng/",
        "https://rppa-appr.ca/eng/passenger-help",
        "https://rppa-appr.ca/eng/notices",
        "https://rppa-appr.ca/eng/archives",
        "https://rppa-appr.ca/eng/right/other-air-traveller-rights-and-information",
    ]

    loader = RecursiveUrlLoader(URL, max_depth=3, use_async=True, timeout=99)

    docs_list = []
    for doc in loader.lazy_load():
        if doc.metadata['source'] in EXCLUDE_URLS:
            continue

        lc_docs = lc_html_split(doc.page_content)

        if len(lc_docs) > 1:
            docs_list.extend(
                [
                    {**doc.metadata, "text": lc_doc.page_content, **lc_doc.metadata}
                    for lc_doc in lc_docs
                ]
            )
            continue

        elements = partition_html(text=doc.page_content, skip_headers_and_footers=True)

        to_remove = ["This node", "Make a complaint", "MP3", "Listen to text"]
        elements = [e for e in elements if not any(e.text.startswith(prefix) for prefix in to_remove)]

        end_idx = len(elements)
        for i, e in enumerate(reversed(elements)):
            if (
                any(
                    e.text.startswith(prefix)
                    for prefix in [
                        "Notices",
                        "Related Links",
                        "Reference: ",
                        "Resource Guides",
                        "Resource guide",
                    ]
                )
                and len(elements) - i - 1 < end_idx
            ):
                end_idx = len(elements) - i - 1

        text = format_parsed_html_as_md(elements[:end_idx])

        lc_docs = lc_markdown_split(text)

        if len(lc_docs) >= 1:
            docs_list.extend(
                [
                    {**doc.metadata, "text": lc_doc.page_content, **lc_doc.metadata}
                    for lc_doc in lc_docs
                ]
            )
            continue

        print("Count not split the document: ", doc.metadata["source"])

    logging.info(f"Scraped {len(docs_list)} documents from rppa-appr.ca")

    return pd.DataFrame(docs_list)


def identify_airtravel_issue(df: pd.DataFrame) -> pd.DataFrame:
    # identify the issue of each document based on the key words in the text
    issues_key_words = {
        "flight delays and cancellations": ["flight-delay", "flight-cancellation"],
        "lost, damaged or delayed baggage": ["baggage"],
        "denied boarding": ["boarding"],
    }

    def identify_issue(row):
        for issue, key_words in issues_key_words.items():
            if any(kw in row["source"] for kw in key_words):
                return issue
        return "other"

    df["issue"] = df.apply(identify_issue, axis=1)
    return df

def save_docs_as_md(df: pd.DataFrame, path: Path) -> None:
    # save each document to a separate file with the name of the source

    def save_doc(row):
        _path = path / urlparse(row["source"]).path.lstrip("/").replace("/", "_")
        if not _path.exists():
            _path.mkdir(parents=True)

        filename = row.name

        with open(_path / f"{filename}.md", "w") as f:
            metadata_str = "\n\n".join([f"{k}: {v}" for k, v in row.items() if k != "text"])
            _str = f"{metadata_str}\n\n{row['text']}"
            f.write(_str)
    df.apply(save_doc, axis=1)

    logging.info(f"Saved {len(df)} documents to {path}")

def save_docs_as_json(df: pd.DataFrame, path: Path) -> None:
    # save each document to a separate file with the name of the source

    def save_doc(row):
        _path = path / urlparse(row["source"]).path.lstrip("/").replace("/", "_")
        if not _path.exists():
            _path.mkdir(parents=True)

        filename = row.name

        with open(_path / f"{filename}.json", "w") as f:
            row.to_json(f, indent=4)
    df.apply(save_doc, axis=1)

    logging.info(f"Saved {len(df)} documents to {path}")

# Main function
def main():

    SAVE_PATH = DATA_DIR / "kb" / "docs"

    docs_df = pd.concat([
        scrape_airpassengerrights_ca(),
        scrape_rppa_appr_ca(),
    ])

    docs_df = docs_df[docs_df.text.str.len() > 40].reset_index(drop=True)

    docs_df = identify_airtravel_issue(docs_df)

    # save the documents to subfolders based on the issue
    for issue in docs_df["issue"].unique():
        save_docs_as_json(docs_df[docs_df["issue"] == issue], SAVE_PATH / issue)
        save_docs_as_md(docs_df[docs_df["issue"] == issue], SAVE_PATH / issue)

    docs_df.to_csv(DATA_DIR / "kb" / "docs.csv", index=False)

    return 0

if __name__ == "__main__":
    sys.exit(main())
