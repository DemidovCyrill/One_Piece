class Character:
    def __init__(self, name, jap_name, first_appearance, occupations, residences, affiliations, url, birth_date, age):
        self.name = name
        self.jap_name = jap_name
        self.first_appearance = first_appearance
        self.occupations = occupations
        self.residences = residences
        self.affiliations = affiliations
        self.url = url
        self.birth_date = birth_date
        self.age = age

    def __str__(self):
        return f"{self.name}, {self.url}"

    def __repr__(self):
        return str(self)


