from transformers import pipeline, T5Tokenizer, TFT5ForConditionalGeneration, DistilBertTokenizer, TFDistilBertModel


def summarization_model_init():
    # tokenizer = T5Tokenizer.from_pretrained("arthd24/wanderwise_summary_1", legacy=False)
    # model = TFT5ForConditionalGeneration.from_pretrained("arthd24/wanderwise_summary_1")
    # return tokenizer, model
    return pipeline('summarization', model="arthd24/wanderwise_summary_1")


def classification_model_init():
    # tokenizer = DistilBertTokenizer.from_pretrained("arthd24/wanderwise_classification_1")
    # model = TFDistilBertModel.from_pretrained("arthd24/wanderwise_classification_1")
    # return tokenizer, model
    return pipeline("text-classification", model="arthd24/wanderwise_classification_1")