from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification


def summarization_model_init():
    return pipeline('summarization', model="arthd24/wanderwise_summary_1")


def classification_model_init():
    return pipeline("text-classification", model="arthd24/wanderwise_classification_1")


def ner_model_init():
    return pipeline("token-classification", model="cahya/bert-base-indonesian-NER")