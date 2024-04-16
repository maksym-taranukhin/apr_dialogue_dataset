from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List

class BaseScrapper(ABC):
    """
    The Strategy interface declares operations common to all data scrappers.
    """
    preprocessors = []

    @abstractmethod
    def scrap(self, urls: List) -> List:
        """
        Scrape the website.
        """
        pass

    def preprocess(self, doc) -> str:
        """
        Apply all preprocessors to the text.
        """
        for preprocessor in self.preprocessors:
            doc = preprocessor(doc)
        return doc
