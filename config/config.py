from transformers import pipeline
from mongoengine import connect
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os

load_dotenv()

def db_connect():
    connect(db=os.environ.get("DB_NAME"), host=os.environ.get("DB_URI"))

def firebase_init():
    # Use a service account.
    cred = credentials.Certificate(os.environ.get("SERVICE_ACCOUNT_KEY"))

    app = firebase_admin.initialize_app(cred)

    db = firestore.client()

    return app, db


def summarization_model_init():
    return pipeline('summarization', model="arthd24/wanderwise_summary_1", framework="tf")


def classification_model_init():
    return pipeline("text-classification", model="arthd24/wanderwise_classification_1",  framework="tf")


def ner_model_init():
    return pipeline("token-classification", model="cahya/bert-base-indonesian-NER")