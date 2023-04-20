class SimpleObject:
    def __init__(self, name, jap_name, images):
        self.name = name
        self.jap_name = jap_name
        self.images = images

    def __str__(self):
        return f"{self.name} ({self.jap_name})"

    def __repr__(self):
        return str(self)


class Character(SimpleObject):
    def __init__(self, name, jap_name, first_appearance, occupations,
                 residences, affiliations, url, birth_date, age, bounty, images):
        super().__init__(name, jap_name, images)

        self.first_appearance = first_appearance
        self.occupations = occupations
        self.residences = residences
        self.affiliations = affiliations
        self.url = url
        self.birth_date = birth_date
        self.age = age
        self.bounty = bounty


class Place(SimpleObject):
    def __init__(self, name, jap_name, first_appearance, region, images):
        super().__init__(name, jap_name, images)

        self.first_appearance = first_appearance
        self.region = region


class Article:
    def __init__(self, title, url):
        self.title = title
        self.url = url

    def __str__(self):
        return f"{self.title} - {self.url}"

    def __repr__(self):
        return str(self)
