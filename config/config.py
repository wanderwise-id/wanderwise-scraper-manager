from transformers import pipeline
from dotenv import load_dotenv
import firebase_admin
import os

load_dotenv()

def firebase_init():
    # Use a service account.
    cred = firebase_admin.credentials.Certificate(os.environ.get("SERVICE_ACCOUNT_KEY"))

    app = firebase_admin.initialize_app(cred, {
        'databaseURL': os.environ.get("FIREBASE_URL")
    })

    return app


def summarization_model_init():
    return pipeline('summarization', model="arthd24/wanderwise_summary_1", framework="tf")


def classification_model_init():
    return pipeline("text-classification", model="arthd24/wanderwise_classification_1",  framework="tf")


def ner_model_init():
    return pipeline("token-classification", model="cahya/bert-base-indonesian-NER")