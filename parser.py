from bs4 import BeautifulSoup as bs
import requests

from article import *
from character import *


class Parser:
    def __init__(self, lang: str = "ru"):
        self.url = 'https://onepiece.fandom.com/%lang/wiki/Служебная:Поиск?query=%req'
        self.lang = lang

        self.url = self.url.replace("%lang", self.lang)

    def search_article_by_name(self, request: str, max_results: int = 5):
        url = self.url
        url = url.replace("%req", request)

        r = requests.get(url)
        soup = bs(r.text, "html.parser")

        existing_page_notification = soup.find("p", class_="mw-search-exists")

        articles = []

        if existing_page_notification:
            redirect = existing_page_notification.find("a", href=True)

            article_title = redirect.get("title")
            article_url = url.split(f"/{self.lang}")[0] + redirect.get("href")

            article = Article(title=article_title, url=article_url)
            articles.append(article)

        search_results = soup.find_all("li", class_="unified-search__result")
        search_results = search_results[:max_results - len(articles)]\
            if len(search_results) > max_results else search_results

        for result in search_results:
            result = result.find("a", class_="unified-search__result__title")

            article_title = result.get("data-title")
            article_url = result.get("href")

            article = Article(title=article_title, url=article_url)
            articles.append(article)

        return articles

    @staticmethod
    def get_character_info(article: Article):
        r = requests.get(article.url)
        soup = bs(r.text, "html.parser")

        tags = soup.find("div", class_="page-header__categories").get_text().strip()

        if "люди" not in tags.lower():
            return

        name = soup.find("h2", attrs={"data-source": "name"}).get_text().strip()
        jap_name = soup.find("div", attrs={"data-source": "jname"}).find("div").get_text().strip()

        first_appearance = soup.find("div", attrs={"data-source": "first"}).find("div")
        [sup.extract() for sup in first_appearance.find_all("sup")]
        first_appearance = first_appearance.get_text().strip()

        occupations = soup.find("div", attrs={"data-source": "occupation"}).find("div")
        [sup.extract() for sup in occupations.find_all("sup")]
        occupations = occupations.get_text().strip()

        residences = soup.find("div", attrs={"data-source": "residence"}).find("div")
        [sup.extract() for sup in residences.find_all("sup")]
        residences = residences.get_text().strip()

        affiliations = soup.find("div", attrs={"data-source": "affiliation"}).find("div")
        [sup.extract() for sup in affiliations.find_all("sup")]
        affiliations = affiliations.get_text().strip()

        birth_date = soup.find("div", attrs={"data-source": "birth"}).find("div")
        [sup.extract() for sup in birth_date.find_all("sup")]
        birth_date = birth_date.get_text().strip()

        age = soup.find("div", attrs={"data-source": "age"}).find("div")
        [sup.extract() for sup in age.find_all("sup")]
        age = age.get_text().strip()

        character = Character(name=name, jap_name=jap_name, first_appearance=first_appearance, occupations=occupations,
                              residences=residences, affiliations=affiliations, url=article.url, birth_date=birth_date,
                              age=age)
        return character

    def search_character_by_name(self, request: str):
        articles = self.search_article_by_name(request)
        for article in articles:
            character = self.get_character_info(article)

            if character:
                return character

        return articles
    
