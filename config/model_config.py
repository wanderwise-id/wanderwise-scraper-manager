from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
from mongoengine import connect
from dotenv import load_dotenv
import os

load_dotenv()

def db_connect():
    connect(db=os.environ.get("DB_NAME"), host=os.environ.get("DB_URI"))


def summarization_model_init():
    return pipeline('summarization', model="arthd24/wanderwise_summary_1")


def classification_model_init():
    return pipeline("text-classification", model="arthd24/wanderwise_classification_1")


def ner_model_init():
    return pipeline("token-classification", model="cahya/bert-base-indonesian-NER")