from bs4 import BeautifulSoup

def extract_urls(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    urls = [a['href'] for a in soup.find_all('a', href=True)]
    return urls

def filter_relevant_urls(urls, html_content, keywords):
    relevant_urls = []
    for url in urls:
        surrounding_text = get_surrounding_text(url, html_content)
        if any(keyword.lower() in surrounding_text.lower() or keyword.lower() in url.lower() for keyword in keywords):
            relevant_urls.append(url)
    return relevant_urls

def get_surrounding_text(url, html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    link = soup.find('a', href=url)
    if link:
        surrounding_text = link.get_text()
        parent_text = link.find_parent().get_text()
        return surrounding_text + " " + parent_text
    return ""
