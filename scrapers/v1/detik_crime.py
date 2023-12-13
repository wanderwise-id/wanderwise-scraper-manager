from models.scraper_setting import ScraperSetting
from models.article import Article
from bs4 import BeautifulSoup
import requests
import main


class DetikCrimeScraper():
    name = "detik-crime-scraper"

    def run(self):
        setting = ScraperSetting.objects(name=self.name).first()

        if setting == None:
            return

        if setting.status == False:
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
                except Exception as e:
                    print("sub article : ", e)

        except Exception as e:
            print("all article : ", e)
