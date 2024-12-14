import requests
import logging
from typing import Optional, Dict, Any
from bs4 import BeautifulSoup
import time
import random


class BaseScraper:
    """
    A base class for web scraping with common functionality and best practices.
    """

    def __init__(
        self,
        base_url,
        headers: Optional[Dict[str, str]] = None,
        max_retries: int = 3,
        timeout: int = 10,
        delay_range: tuple = (1, 3),
    ):
        """
        Initialize the base scraper with configuration options.

        :param base_url: Base URL of the website to scrape
        :param headers: Custom headers for requests (optional)
        :param max_retries: Maximum number of retry attempts for failed requests
        :param timeout: Request timeout in seconds
        :param delay_range: Random delay range between requests (min, max)
        """
        self.base_url = base_url
        self.headers = headers or {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }
        self.max_retries = max_retries
        self.timeout = timeout
        self.delay_range = delay_range

        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger(self.__class__.__name__)

    def make_request(self, url: str) -> Optional[BeautifulSoup]:
        """
        Make a robust HTTP request with retry mechanism and error handling.

        :param url: Full URL to scrape
        :return: BeautifulSoup object or None if request fails
        """
        for attempt in range(self.max_retries):
            try:
                # Add random delay between requests
                time.sleep(random.uniform(*self.delay_range))

                # Make the request
                response = requests.get(url, headers=self.headers, timeout=self.timeout)

                # Raise an exception for bad status codes
                response.raise_for_status()

                # Parse with BeautifulSoup
                return BeautifulSoup(response.content, "html.parser")

            except requests.exceptions.RequestException as e:
                self.logger.warning(
                    f"Request failed (Attempt {attempt + 1}/{self.max_retries}): {e}"
                )

                # If it's the last attempt, log the error
                if attempt == self.max_retries - 1:
                    self.logger.error(
                        f"Failed to fetch {url} after {self.max_retries} attempts"
                    )
                    return None

                # Exponential backoff
                time.sleep(2**attempt)

        return None

    def extract_text(self, element: Any, default: str = "") -> str:
        """
        Safely extract text from a BeautifulSoup element.

        :param element: BeautifulSoup element
        :param default: Default value if text extraction fails
        :return: Extracted text or default value
        """
        try:
            return element.get_text(strip=True) if element else default
        except Exception as e:
            self.logger.warning(f"Text extraction failed: {e}")
            return default

    def scrape(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Abstract method to be implemented by specific scrapers.

        :param url: URL to scrape
        :return: Extracted data or None
        """
        raise NotImplementedError("Subclasses must implement the scrape method")
