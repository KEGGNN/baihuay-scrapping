from typing import Optional, Dict, Any, List
import time
import random

from src.scrapers.base_scraper import BaseScraper


class ThaiRathNewsScraper(BaseScraper):
    def __init__(self):
        super().__init__("https://www.thairath.co.th/news/")
        self.news_category = [
            "royal",
            "society",
            "politic",
            "money",
            "foreign",
            "crime",
        ]

    def scrape(self, url):
        for category in self.news_category:
            self.scrape_highlight_news(f"{self.base_url}{category}")
            time.sleep(random.uniform(*self.delay_range))

    def scrape_highlight_news(
        self, url: str, category: str
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Scrap highlight news in carrousel for each category

        :param url: URL to scrape
        :return: Extracted data
        """
        soup = self.make_request(url)
        if not soup:
            return None

        highlight_news = soup.find("div", {"class": "slick-track"}).find_all("a")

        highlight_news_data = []
        for news in highlight_news:
            news_content_link = f"{url}{news.get('href')}"
            highlight_news_data.append(
                {
                    "title": news.get("title"),
                    "link": news_content_link,
                    "news_type": category,
                    "content": self.scrape_news_content(news_content_link),
                }
            )
        return highlight_news_data

    def scrape_news_content(self, url: str) -> Optional[List[Dict[str, Any]]]:
        """
        Scrap highlight news in carrousell for each category

        :param url: URL to scrape
        :return: Extracted data
        """
        soup = self.make_request(url)
        if not soup:
            return None

        news_content_scrap = soup.find("div", {"class": "article-body"}).find_all("p")
        new_content = ""
        for line in news_content_scrap:
            new_content += line.getText()
        return new_content
