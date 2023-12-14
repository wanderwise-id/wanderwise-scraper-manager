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

load_dotenv()


class DetikCrimeScraper():
    name = "detik-crime-scraper"

    def run(self):
        summarizer = Summarizer()
        classifier = Classifier()
        ner = NER()
        translator = GoogleTranslator(source='id', target='en')
        setting = ScraperSetting.objects(name=self.name).first()

        if setting is None:
            return

        if not setting.status:
            return

        try:
            html_content = requests.get('https://www.detik.com/bali/hukum-kriminal/indeks/1')
            soup = BeautifulSoup(html_content.content, 'lxml')

            article_list = soup.find_all('article', class_='list-content__item')

            for article in article_list:
                identical_article_amount = Article.objects(link_to_origin=article.a["href"]).count()
                if identical_article_amount > 0:
                    break

                try:
                    html_content = requests.get(article.a["href"])
                    soup = BeautifulSoup(html_content.content, 'lxml')

                    # preprocess cleansing
                    if soup.find_all('p', class_='para_caption'):
                        for i in range(len(soup.find_all('p', class_='para_caption'))):
                            soup.find('p', class_='para_caption').decompose()

                    content = ' '.join([translator.translate(p.text) for p in soup.find_all('p')]).strip()
                    locations = ner.generate(content)
                    if not locations:
                        continue

                    for location in locations:
                        if City.objects(name=location).count() > 0:

                            title = translator.translate(
                                (soup.find('h1', class_='detail__title')).text.strip().replace("\n", ""))
                            summarize = summarizer.generate(content)
                            category = classifier.generate(summarize)

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
                                "date_published": date,
                                "location": locations,
                                "timezone": timezone,
                                "image": image
                            }
                            article_obj = Article(**article_dict)
                            article_obj.save()
                            break
                except Exception as e:
                    print("sub article : ", e)

        except Exception as e:
            print("all article : ", e)
