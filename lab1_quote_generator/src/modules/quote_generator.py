import random

class QuoteGenerator:
    def __init__(self, quotes):
        self.quotes = quotes

    def random_quote(self):
        return random.choice(self.quotes)
