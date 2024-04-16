from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_text_splitters import HTMLHeaderTextSplitter

html_headers_to_split_on = [
    ("h1", "header 1"),
    ("h2", "header 2"),
    ("h3", "header 3"),
]
markdown_headers_to_split_on = [
    ("#", "header 1"),
    ("##", "header 2"),
    ("###", "header 3"),
]

markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=markdown_headers_to_split_on)
html_splitter = HTMLHeaderTextSplitter(headers_to_split_on=html_headers_to_split_on)

def filter_by_url(doc, exclude_urls):
    """
    Exclude documents by URL.
    """
    if doc.metadata["source"] not in exclude_urls:
        return doc
    return None


def split_by_html_headers(doc):
    """
    Split document by HTML headers.
    """
    splitted_docs = [d for d in html_splitter.split_text(doc.page_content)]

    # update metadata for each splitted document with the original metadata
    for d in splitted_docs:
        d.metadata.update(doc.metadata)

    return [d for d in splitted_docs if d.metadata and "Header 1" in d.metadata]


def split_by_markdown_headers(doc):
    """
    Split document by Markdown headers.
    """
    splitted_docs = [d for d in markdown_splitter.split_text(doc.page_content)]

    # update metadata for each splitted document with the original metadata
    for d in splitted_docs:
        d.metadata.update(doc.metadata)

    return splitted_docs