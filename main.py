from contextlib import asynccontextmanager
from config.model_config import *
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # initialize model
    global classifier
    global summarizer

    classifier = classification_model_init()
    summarizer = summarization_model_init()

    yield

    # when shutdown
    del classifier
    del summarizer

app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.get("/test-summarization-model")
async def test_model():
    text = 'summarize: A 95 year old grandmother was raped by a 65 year old grandfather with the initials MH in Bekasi, West Java. This depraved act was discovered by the victims nephew with the initials R (65). Quoted from detikNews, Head of Criminal Investigation Unit for the Bekasi Metro Police, Commissioner Gogo Galesung, said the incident occurred on Sunday (5/2/2023) afternoon.  At that time, R was about to deliver rice, but instead caught the victim being raped. "So his nephew caught him wanting to deliver rice," said Gogo, Tuesday (7/3/2023). Gogo has not clearly detailed the complete chronology of the perpetrators depraved actions. However, he said the perpetrator had now been arrested. Meanwhile, the grandmother reportedly fell ill after being raped. Because of these conditions, Gogo Galesung said the police had not been able to ask the rape victim for information. "And the grandmother is also senile and has minimal witnesses. Her nephew caught her afterwards," added Gogo. Apart from the victim, the grandfather of the perpetrator of the rape was also sick. Grandpa is currently being taken to the hospital. "The grandfather is also sick, his body is dropping," he added. Viral on Social Media The incident went viral on social media. In the video footage circulating, a number of residents can be seen gathered around the victims bamboo-walled house, which is not far from the house of the perpetrator MH. "Astagfirullahalazim... really depraved," said a man in the video recording. It was narrated that the victim was raped in her house by MH. This incident was discovered by R. The nephew cried until he said istigfar. Immediately spotted by the victims nephew, the perpetrator stood up. From the narrative on social media, it was stated that the victim was not wearing any clothes. Meanwhile, the perpetrator only wore a t-shirt, no trousers.'
    outputs = summarizer(text)

    return {
        "message": "successfuly summarizing",
        "data": outputs
    }


@app.get("/test-classification-model")
async def test_model():
    text: str = "A 95 year old grandmother was raped by a 65 year old grandfather with the initials MH in Bekasi, West Java. This depraved act was discovered by the victims nephew with the initials R"
    outputs = classifier(text)

    return {
        "message": "successfuly classify",
        "data": outputs
    }