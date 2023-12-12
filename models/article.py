from mongoengine import *


class Article(Document):
    title = StringField(required=True)
    summarize = StringField(required=True)
    link_to_origin = StringField(require=True)
    category = StringField(required=True)
    date_published = DateTimeField(required=True)
    location = StringField(required=True)
    timezone = StringField(required=True)
