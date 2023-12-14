from mongoengine import *

class City(Document):
    name = StringField(required=True)
    province = StringField(required=True)
    country = StringField(required=True)