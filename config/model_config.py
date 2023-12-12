from transformers import pipeline


def summarization_model_init():
    return pipeline('summarization', model="arthd24/wanderwise_summary_1")


def classification_model_init():
    return pipeline("text-classification", model="arthd24/wanderwise_classification_1")
