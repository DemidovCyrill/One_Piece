class Article:
    def __init__(self, title, url):
        self.title = title
        self.url = url

    def __str__(self):
        return f"{self.title}, {self.url}"

    def __repr__(self):
        return str(self)
