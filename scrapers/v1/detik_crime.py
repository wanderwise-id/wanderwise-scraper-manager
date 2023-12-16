from time import sleep

from google.cloud.firestore_v1 import FieldFilter
from models.scraper_setting import ScraperSetting
from models.article import Article
from models.city import City
from helper.summarizer import Summarizer
from helper.classifier import Classifier
from helper.ner import NER
from bs4 import BeautifulSoup
import requests
from deep_translator import GoogleTranslator
from datetime import datetime
from dotenv import load_dotenv
import os
import json
import main
from firebase_admin import db
from firebase_admin import firestore

load_dotenv()


class DetikCrimeScraper():
    name = "detik-crime-scraper"

    def run(self):
        print("hello")
        summarizer = Summarizer()
        classifier = Classifier()
        ner = NER()
        translator = GoogleTranslator(source='id', target='en')
        setting = db.reference("/settings/{name}".format(name=self.name)).get()
        #setting = ScraperSetting.objects(name=self.name).first()

        if not setting['status']:
            print("disable service")
            return

        try:
            html_content = requests.get('https://www.detik.com/bali/hukum-kriminal/indeks/1')
            soup = BeautifulSoup(html_content.content, 'lxml')

            article_list = soup.find_all('article', class_='list-content__item')

            for article in article_list:
                # mongodb code : check amount of article
                # identical_article_amount = Article.objects(link_to_origin=article.a["href"]).count()
                # if identical_article_amount > 0:
                #     break

                try:
                    html_content = requests.get(article.a["href"])
                    soup = BeautifulSoup(html_content.content, 'lxml')

                    # preprocess cleansing
                    if soup.find_all('p', class_='para_caption'):
                        for i in range(len(soup.find_all('p', class_='para_caption'))):
                            soup.find('p', class_='para_caption').decompose()

                    content = ""
                    title = ""
                    translate_success = False

                    while not translate_success:
                        try:
                            content = ' '.join([translator.translate(p.text) for p in soup.find_all('p')]).strip()
                            title = translator.translate(
                                (soup.find('h1', class_='detail__title')).text.strip().replace("\n", ""))
                            translate_success = True
                        except Exception as e:
                            print("translation : ", e)
                            sleep(1)

                    locations = ner.generate(content)

                    if not locations:
                        continue

                    print(locations)
                    for location in locations:
                        # mongodb code : check is city available
                        # if City.objects(name=location).count() > 0:
                        city = db.reference("/cities/{location}".format(location=location)).get()

                        if not city:
                            print("doesn't have collection of cities")
                            continue

                        collection_of_news = (db.reference("/news")
                                              .child(location)
                                              .order_by_child("link_to_origin")
                                              .equal_to(article.a["href"])
                                              .get())
                        print("collection of news : ", collection_of_news)

                        if collection_of_news:
                            break

                        summarize = summarizer.generate(content)
                        category = classifier.generate(summarize)

                        if category.find("Other") != -1:
                            break

                        date_string, timezone = (soup.find('div', class_='detail__date')).string.rsplit(' ', 1)
                        date = None

                        for date_format in ["%d %b %Y %H:%M", "%b %d %Y %H:%M", "%b %d, %Y %H:%M"]:
                            try:
                                date_string = translator.translate(date_string)
                                date_string = (date_string.split(" "))
                                del date_string[0]
                                date_string = " ".join(date_string)
                                date = datetime.strptime(date_string, date_format)
                                break
                            except Exception as e:
                                print(f"failed : {e}")

                        image = {}

                        try:
                            img_link = soup.find("figure", class_="detail__media-image").img["src"]
                            response = requests.get(img_link)
                            response = requests.post("".join(["https://api.imgbb.com/1/upload?key=",
                                                              os.environ.get("IMGBB_API_KEY")]),
                                                     files={'image': response.content})

                            data = json.loads(response.content)

                            image = {
                                "url": data["data"]["url"],
                                "thumb": data["data"]["thumb"]["url"],
                                "delete_url": data["data"]["delete_url"]
                            }
                        except Exception as e:
                            print("image gathering : ", e)

                        article_dict = {
                            "title": title,
                            "summarize": summarize,
                            "link_to_origin": article.a["href"],
                            "category": category,
                            "date_published": str(date),
                            "location": locations,
                            "timezone": timezone,
                            "image": image
                        }
                        print(article_dict)
                        # mongodb code : unpack dictionary and save data
                        # article_obj = Article(**article_dict)
                        # article_obj.save()
                        # print(article_dict)
                        # for city in cities:
                        #     city_ref = main.fb_db.collection("cities").document(city.get("idCity"))
                        #     city_ref.collection("news").add(article_dict)
                        (db.reference("news").child(location).push(article_dict))
                        break
                except Exception as e:
                    print("sub article : ", e)

        except Exception as e:
            print("all article : ", e)
