from firebase_admin import db
from datetime import datetime

def score_updater(location:str):
    city_news = db.reference("news").child(location).get()
    weights = db.reference("weights").get()

    data = {}
    total_case = 0

    for category_news in city_news.values():
        for news in category_news.values():
            date = datetime.strptime(news["date_published"],"%Y-%m-%d %H:%M:%S")
            if date.year == datetime.now().year:
                category = news["category"].lower().replace(" ", "_")
                if category not in data:
                    data[category] = 0

                    data[category] += 1
                    total_case += 1

    weighted_sum = 0
    for data_key in data:
        data_key = data_key.lower().replace(" ", "_")
        weighted_sum += data[data_key] * weights[data_key]

    safety_score = 100 - (weighted_sum/total_case) * 100

    score = {
        "score": safety_score,
        "datetime": str(datetime.now()),
        "description": "-"
    }

    db.reference("scores").child("Denpasar").push(score)