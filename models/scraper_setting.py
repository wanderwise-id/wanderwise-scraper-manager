from mongoengine import *


class ScraperSetting(Document):
    name = StringField(required=True)
    status = BooleanField(required=True, default=False)
