from queue import Queue
from config import load_config
from scraper import fetch_and_convert, clean_markdown
from text_processing import advanced_text_splitter
from url_extraction import extract_urls, filter_relevant_urls
from document_storage import save_documents

def main():
    visited_urls = set()
    url_queue = Queue()
    config = load_config('configs/config.yml')
    
    initial_url = config['initial_url']
    query_keywords = config['query_keywords']
    
    url_queue.put(initial_url)
    visited_urls.add(initial_url)
    
    while not url_queue.empty():
        print(f"Queue size: {url_queue.qsize()}")
        url = url_queue.get()
        print(f"Processing URL: {url}")
        markdown_output, html_content = fetch_and_convert(url)
        if markdown_output and html_content:
            cleaned_output = clean_markdown(markdown_output)
            docs = advanced_text_splitter(cleaned_output)
            save_documents(docs)

            urls = extract_urls(html_content)
            relevant_urls = filter_relevant_urls(urls, html_content, query_keywords)
            for new_url in relevant_urls:
                if new_url not in visited_urls:
                    url_queue.put(new_url)
                    visited_urls.add(new_url)

if __name__ == "__main__":
    main()
