from bs4 import BeautifulSoup as bs
import requests

from objects import *


class Parser:
    def __init__(self, lang: str = "ru"):
        self.url = 'https://onepiece.fandom.com/%lang/wiki/Служебная:Поиск?query=%req'
        self.lang = lang

        self.url = self.url.replace("%lang", self.lang)

    def search_articles(self, request: str, max_results: int = 5):
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

        allowed_tags = ["люд", "персонаж", "челове"]
        if not any(filter(lambda tag: tag in tags.lower(), allowed_tags)):
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

        images_src = soup.find("nav", attrs={"data-item-name": "gallery"})
        if images_src:
            images_src = images_src.find_all("a", class_="image")
            images_src = [img.get("href") for img in images_src]
        else:
            images_src = soup.find("a", class_="image")
            images_src = [images_src.get("href")]

        images = [requests.get(url).content for url in images_src]

        character = Character(name=name, jap_name=jap_name, first_appearance=first_appearance, occupations=occupations,
                              residences=residences, affiliations=affiliations, url=article.url, birth_date=birth_date,
                              age=age, images=images)
        return character

    def search_character_by_name(self, request: str):
        articles = self.search_articles(request)
        for article in articles:
            character = self.get_character_info(article)

            if character:
                return character

        return articles

    @staticmethod
    def get_place_info(article: Article):
        r = requests.get(article.url)
        soup = bs(r.text, "html.parser")

        tags = soup.find("div", class_="page-header__categories").get_text().strip()

        allowed_tags = ["мест", "город", "остров", "корол"]
        if not any(filter(lambda tag: tag in tags.lower(), allowed_tags)):
            return

        disallowed_tags = ["люд", "персонаж", "челове"]
        if any(filter(lambda tag: tag in tags.lower(), disallowed_tags)):
            return

        name = soup.find("h2", attrs={"data-source": "name"}).get_text().strip()
        jap_name = soup.find("div", attrs={"data-source": "jname"}).find("div").get_text().strip()

        first_appearance = soup.find("div", attrs={"data-source": "first"}).find("div")
        [sup.extract() for sup in first_appearance.find_all("sup")]
        first_appearance = first_appearance.get_text().strip()

        region = soup.find("div", attrs={"data-source": "region"}).find("div")
        [sup.extract() for sup in region.find_all("sup")]
        region = region.get_text().strip()

        images_src = soup.find("nav", attrs={"data-item-name": "gallery"})
        if images_src:
            images_src = images_src.find_all("a", class_="image")
            images_src = [img.get("href") for img in images_src]
        else:
            images_src = soup.find("a", class_="image")
            images_src = [images_src.get("href")]

        images = [requests.get(url).content for url in images_src]

        place = Place(name=name, jap_name=jap_name, first_appearance=first_appearance, region=region, images=images)

        return place

    def search_place_by_name(self, request: str):
        articles = self.search_articles(request)
        for article in articles:
            place = self.get_place_info(article)

            if place:
                return place

        return articles

    @staticmethod
    def get_object_info(article: Article):
        r = requests.get(article.url)
        soup = bs(r.text, "html.parser")

        # name = soup.find("h1", attrs={"id": "firstHeading"}).get_text().strip()
        name = soup.find("h2", attrs={"data-source": "name"})

        if not name:
            name = soup.find("h2", attrs={"data-source": "title"})

        name = name.get_text().strip()
        jap_name = soup.find("div", attrs={"data-source": "jname"}).find("div").get_text().strip()

        images_src = soup.find("nav", attrs={"data-item-name": "gallery"})
        if images_src:
            images_src = images_src.find_all("a", class_="image")
            images_src = [img.get("href") for img in images_src]
        else:
            images_src = soup.find("a", class_="image")
            images_src = [images_src.get("href")]

        images = [requests.get(url).content for url in images_src]

        object_ = SimpleObject(name=name, jap_name=jap_name, images=images)

        return object_

    def search_object(self, request: str):
        article = self.search_articles(request, max_results=1)[0]

        character = self.get_character_info(article)
        if character:
            return character

        place = self.get_place_info(article)
        if place:
            return place

        return self.get_object_info(article)
