import re
from typing import List

from scrapper import BaseScrapper
from langchain_community.document_loaders.recursive_url_loader import (
    RecursiveUrlLoader,  # noqa
)
from langchain_core.documents import Document

from unstructured.documents.html import HTMLTitle
from unstructured.partition.html import partition_html

from scrapper.preprocessors import filter_by_url, split_by_html_headers, split_by_markdown_headers
from utils import format_parsed_html_as_md

BASE_URLS = [
    # "https://airpassengerrights.ca/en/practical-guides/"
    # "https://airpassengerrights.ca/en/practical-guides/denied-boarding/canada-pre-appr/glossary/glossary-of-terms"
    # "https://airpassengerrights.ca/en/practical-guides/denied-boarding/european-union-and-economic-area/step-by-step-guide"

    # damaged baggage
    "https://airpassengerrights.ca/en/practical-guides/baggage/damage",
    "https://airpassengerrights.ca/en/practical-guides/baggage/damage/step-by-step-guide"
    "https://airpassengerrights.ca/en/practical-guides/baggage/damage/faq",
    # delayed baggage
    "https://airpassengerrights.ca/en/practical-guides/baggage/delay",
    "https://airpassengerrights.ca/en/practical-guides/baggage/delay/step-by-step-guide",
    "https://airpassengerrights.ca/en/practical-guides/baggage/delay/faq",
    # lost baggage
    "https://airpassengerrights.ca/en/practical-guides/baggage/lost",
    "https://airpassengerrights.ca/en/practical-guides/baggage/lost/step-by-step-guide",
    "https://airpassengerrights.ca/en/practical-guides/baggage/lost/faq",
    # baggage glossary
    "https://airpassengerrights.ca/en/practical-guides/baggage/glossary",
]


# exclude the following pages
EXCLUDE_URLS = [
    "https://airpassengerrights.ca/en/practical-guides/",
    "https://airpassengerrights.ca/en/practical-guides/denied-boarding/canada-pre-appr/faq",
    "https://airpassengerrights.ca/en/practical-guides/denied-boarding/canada-pre-appr",
]

INVALID_TITLES = [
    "Tweet",
    "Pin it",
    "Work in progress:",
]

INVALID_PREFIXES = [
    "Step by Step Guide					",
    "Step by Step Guide Follow ",
    "FAQ Find answers",
    "Glossary List of terms",
]

def html_doc_to_md(doc):
    """
    Convert HTML document to markdown.
    """
    elements = partition_html(text=doc.page_content, skip_headers_and_footers=True)
    md_text = format_parsed_html_as_md(elements)
    return Document(md_text, metadata=doc.metadata)

def clean_by_html_elements(doc):
    """
    Clean document by HTML elements.
    """
    elements = partition_html(text=doc.page_content, skip_headers_and_footers=True)

    start_idx = 0
    for i, e in enumerate(elements):
        if isinstance(e, HTMLTitle):
            start_idx = i
            break

    end_idx = len(elements)
    for i, e in enumerate(reversed(elements)):
        if isinstance(e, HTMLTitle):
            is_invalid_title = e.text in INVALID_TITLES
            is_invalid_prefix = any(e.text.startswith(prefix) for prefix in INVALID_PREFIXES)
            if is_invalid_title or is_invalid_prefix:
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

    return Document(text, metadata=doc.metadata)

def split_by_headers(doc):
    """
    Split document by headers.
    """
    splitted_docs = split_by_html_headers(doc)
    if len(splitted_docs) > 1:
        return splitted_docs

    clean_doc = clean_by_html_elements(doc)
    splitted_docs = split_by_markdown_headers(clean_doc)

    if len(splitted_docs) > 1:
        return splitted_docs

    return [doc]


class APRScrapper(BaseScrapper):
    """
    A scrapper for https://airpassengerrights.ca/en/
    """
    def __init__(self):
        self.preprocessors = [
            lambda doc: filter_by_url(doc, EXCLUDE_URLS),
            # split_by_headers,
            # html_doc_to_md,
            clean_by_html_elements
        ]

    def scrap(self, urls: List = BASE_URLS) -> List:
        """
        Scrape the APR website.
        """
        docs_list = []
        for url in urls:
            loader = RecursiveUrlLoader(url, max_depth=99999, use_async=False, timeout=99)

            # load and preprocess the documents
            docs = [self.preprocess(doc) for doc in loader.lazy_load()]

            # merge list of lists if any
            if any(isinstance(doc, list) for doc in docs):
                docs = sum(docs, [])

            # flatten docs into a list of dictionaries and store them
            docs_list += [
                {"text": doc.page_content, **doc.metadata}
                for doc in docs if doc
            ]

        return docs_list
