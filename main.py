import datetime
import os
from contextlib import asynccontextmanager

import requests
from google.cloud.firestore_v1 import FieldFilter

from config.config import *
from fastapi import FastAPI
from models.article import Article
from scrapers.v1.detik_crime import DetikCrimeScraper
from firebase_admin import firestore
from firebase_admin import db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # initialize model
    global classifier
    global summarizer
    global ner
    global fb_app

    classifier = classification_model_init()
    summarizer = summarization_model_init()
    ner = ner_model_init()
    fb_app = firebase_init()

    # connect to db
    # db_connect()

    yield

    # when shutdown
    del classifier, summarizer, ner
    del fb_app


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.get("/test-summarization-model")
async def test_model():
    text = 'summarize: A 95 year old grandmother was raped by a 65 year old grandfather with the initials MH in Bekasi, West Java. This depraved act was discovered by the victims nephew with the initials R (65). Quoted from detikNews, Head of Criminal Investigation Unit for the Bekasi Metro Police, Commissioner Gogo Galesung, said the incident occurred on Sunday (5/2/2023) afternoon.  At that time, R was about to deliver rice, but instead caught the victim being raped. "So his nephew caught him wanting to deliver rice," said Gogo, Tuesday (7/3/2023). Gogo has not clearly detailed the complete chronology of the perpetrators depraved actions. However, he said the perpetrator had now been arrested. Meanwhile, the grandmother reportedly fell ill after being raped. Because of these conditions, Gogo Galesung said the police had not been able to ask the rape victim for information. "And the grandmother is also senile and has minimal witnesses. Her nephew caught her afterwards," added Gogo. Apart from the victim, the grandfather of the perpetrator of the rape was also sick. Grandpa is currently being taken to the hospital. "The grandfather is also sick, his body is dropping," he added. Viral on Social Media The incident went viral on social media. In the video footage circulating, a number of residents can be seen gathered around the victims bamboo-walled house, which is not far from the house of the perpetrator MH. "Astagfirullahalazim... really depraved," said a man in the video recording. It was narrated that the victim was raped in her house by MH. This incident was discovered by R. The nephew cried until he said istigfar. Immediately spotted by the victims nephew, the perpetrator stood up. From the narrative on social media, it was stated that the victim was not wearing any clothes. Meanwhile, the perpetrator only wore a t-shirt, no trousers.'
    outputs = summarizer(text)

    return {
        "message": "successfuly summarizing",
        "data": outputs
    }


@app.get("/test-classification-model")
async def test_model():
    text: str = "A 95 year old grandmother was raped by a 65 year old grandfather with the initials MH in Bekasi, West Java. This depraved act was discovered by the victims nephew with the initials R"
    outputs = classifier(text)

    return {
        "message": "successfuly classify",
        "data": outputs
    }


@app.get("/test-ner-model")
async def test_model():
    text: str = "A 95 year old grandmother was raped by a 65 year old grandfather with the initials MH in Bekasi, West Java. This depraved act was discovered by the victims nephew with the initials R"
    outputs = ""
    for entity in ner(text):
        if entity['entity'].find("GPE") != -1:
            outputs = entity['word']
            break

    return {
        "message": "successfuly classify",
        "data": outputs
    }


@app.get("/process")
async def test_model():
    text: str = 'summarize: A 95 year old grandmother was raped by a 65 year old grandfather with the initials MH in Bekasi, West Java. This depraved act was discovered by the victims nephew with the initials R (65). Quoted from detikNews, Head of Criminal Investigation Unit for the Bekasi Metro Police, Commissioner Gogo Galesung, said the incident occurred on Sunday (5/2/2023) afternoon.  At that time, R was about to deliver rice, but instead caught the victim being raped. "So his nephew caught him wanting to deliver rice," said Gogo, Tuesday (7/3/2023). Gogo has not clearly detailed the complete chronology of the perpetrators depraved actions. However, he said the perpetrator had now been arrested. Meanwhile, the grandmother reportedly fell ill after being raped. Because of these conditions, Gogo Galesung said the police had not been able to ask the rape victim for information. "And the grandmother is also senile and has minimal witnesses. Her nephew caught her afterwards," added Gogo. Apart from the victim, the grandfather of the perpetrator of the rape was also sick. Grandpa is currently being taken to the hospital. "The grandfather is also sick, his body is dropping," he added. Viral on Social Media The incident went viral on social media. In the video footage circulating, a number of residents can be seen gathered around the victims bamboo-walled house, which is not far from the house of the perpetrator MH. "Astagfirullahalazim... really depraved," said a man in the video recording. It was narrated that the victim was raped in her house by MH. This incident was discovered by R. The nephew cried until he said istigfar. Immediately spotted by the victims nephew, the perpetrator stood up. From the narrative on social media, it was stated that the victim was not wearing any clothes. Meanwhile, the perpetrator only wore a t-shirt, no trousers.'

    article = {}
    article["title"] = "sample"
    article["summarize"] = summarizer(text)[0]['summary_text']
    article["link_to_origin"] = "sample"
    article["category"] = classifier(text)[0]['label']
    article["date_published"] = datetime.datetime.now()
    article["timezone"] = "WIB"

    for entity in ner(text[:511] if len(text) > 511 else text):
        if entity['entity'].find("GPE") != -1:
            article["location"] = entity['word']
            break
    print(article)
    article = Article(**article)
    article.save()

    return {
        "message": "successfuly classify",
        "data": article
    }


@app.get("/detik-crime")
async def scraper():
    scraper = DetikCrimeScraper()
    scraper.run()

    return {
        "message": "successfuly scrape"
    }


@app.get("/firebase_test")
async def firebase():
    # firestore code
    # cities = (fb_db.collection("cities")
    #           .where(filter=FieldFilter("name", "==", "Badung"))
    #           .get())
    #
    # for city in cities:
    #     city_ref = fb_db.collection("cities").document(city.get("idCity"))
    #     city_ref.collection("news").add({"name": "blablabla"})

    ref = db.reference("/cities")
    print(ref.get())
    ref = db.reference("/cities/Denpasar")
    print(ref.get())

    return {
        "message": "why are you gay"
    }


@app.get("/weather_test")
async def weather():
    response = requests.get(
        "https://api.weatherapi.com/v1/current.json?q={location}&key={api_key}".format(location="Denpasar",
                                                                                       api_key=os.environ.get(
                                                                                           "WEATHER_API_KEY")))
    print(response.content)
    return {
        "message": "you are very gay"
    }
