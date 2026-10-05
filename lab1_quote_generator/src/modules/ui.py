class UserInterface:
    def __init__(self, generator):
        self.generator = generator

    def run(self):
        print("Генератор случайных цитат")
        print(self.generator.random_quote()["text"])
