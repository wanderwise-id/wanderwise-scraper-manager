import main
# import geonamescache


class NER():

    def preprocess(self, text: str):
        return text if len(text) < 512 else text[:511]

    def generate(self, text: str):
        # gc = geonamescache.GeonamesCache()
        text = self.preprocess(text)
        gen_kwargs = {}

        ner_result = main.ner(text, **gen_kwargs)
        final_result = []

        if ner_result:
            for place in ner_result:
                if place["entity"].find("GPE") != -1:
                    final_result.append(place["word"].capitalize())
                # city = gc.search_cities(place["word"], case_sensitive=False, contains_search=False)

                # if city[0]:
                #     final_result.append(city[0]["name"])
        return final_result
