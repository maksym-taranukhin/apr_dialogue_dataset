# Web Scraper

## Overview

This project is a web scraper that fetches a web page and searches for specific keywords within the content. The `initial_url` and `query_keywords` are configurable via a `config.yml` file.

## Configuration

The `config.yml` file located in the `configs` directory contains the initial URL and the keywords to search for.

## How to Run

1. Ensure you have the necessary packages installed:

    ```bash
    pip install -r requirements.txt
    ```

2. Run the main script:

    ```bash
    python main.py
    ```

## Scripts

- `config.py`: Reads configuration from the `config.yml` file.
- `session_setup.py`: Sets up the HTTP session with retry strategy.
- `scraper.py`: Contains functions to fetch and clean HTML content, converting it to markdown.
- `text_processing.py`: Contains functions for splitting text into manageable chunks.
- `url_extraction.py`: Contains functions for extracting and filtering URLs from HTML content.
- `document_storage.py`: Contains functions to save processed documents (can be replaced by vector space).
- `main.py`: The main entry point for the application.


