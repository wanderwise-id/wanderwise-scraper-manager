import main


class Classifier():

    def preprocess(self, text: str):
        return text

    def generate(self, text: str):
        text = self.preprocess(text)

        return main.classifier(text)[0]["label"]