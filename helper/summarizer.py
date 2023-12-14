import main

class Summarizer():

    def preprocess(self, text: str):
        prefix = "summarize: "

        return "".join([prefix, text])

    def generate(self, text: str):
        text = self.preprocess(text)

        return main.summarizer(text)[0]['summary_text']