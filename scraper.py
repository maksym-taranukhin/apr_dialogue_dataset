from bs4 import BeautifulSoup
from markdownify import markdownify as md
import re

from session_setup import setup_session

def fetch_and_convert(url):
    try:
        session = setup_session()
        response = session.get(url)
        response.raise_for_status()

        html_content = response.text

        soup = BeautifulSoup(html_content, "html.parser")
        main_content = soup.body
        markdown_text = md(str(main_content))
        return markdown_text, html_content
    except Exception as e:
        print(f"Error processing {url}: {str(e)}")
        return None, None

def clean_markdown(markdown_text):
    soup = BeautifulSoup(markdown_text, "html.parser")
    
    for script_or_style in soup(["script", "style"]):
        script_or_style.decompose()

    text = soup.get_text()
    text = re.sub(r"!\[.*?\]\(.*?\)", "", text)
    text = re.sub(r"\[\]\(.*?\)", "", text)
    text = re.sub(r"\[.*?\]\(.*?\)", "", text)
    text = re.sub(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", "", text)

    lines = text.split("\n")
    cleaned_lines = [line for line in lines if not re.match(r"^\[.*?\]\(.*?\)$", line)]
    cleaned_lines = [line for line in cleaned_lines if not re.search(r"\b(Contact us|Privacy Policy|Copyright|Terms of Service|Advertisement|Sitemap)\b", line) and len(line) > 5]
    cleaned_lines = [line for line in cleaned_lines if not re.search(r"const | let | var | function | \=\>| \(\)| \{\}", line)]

    cleaned_text = "\n".join(cleaned_lines)
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()

    return cleaned_text
