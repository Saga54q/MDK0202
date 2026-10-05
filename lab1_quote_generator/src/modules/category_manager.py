class CategoryManager:
    def categories(self, quotes):
        return sorted({quote.get("category", "Без категории") for quote in quotes})
