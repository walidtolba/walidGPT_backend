from transformers import pipeline
import pyjokes
import pickle
from random import randint
import backend1.settings

classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
summerizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
arabic_to_english = pipeline("translation", model="Helsinki-NLP/opus-mt-ar-en")
english_to_arabic = pipeline("translation", model="marefa-nlp/marefa-mt-en-ar")

with open(r"messaging\poems.bin", "rb") as fp:
    poems = pickle.load(fp)

def generate_poem():
    return poems[randint(0, len(poems) - 1)]

def offline_chat(text, arabic = False):
    if arabic:
        text = arabic_to_english(text)
    labels = ['poem', 'joke', 'summery']
    klass = classifier(text, labels)
    if klass['labels'][0] == 'joke':
        result = pyjokes.get_joke()
    elif klass['labels'][0] == 'poem':
        result = generate_poem()
    elif klass['labels'][0] == 'summery':
        result = summerizer(text)[0]['summary_text'] 
    if arabic:
        result = arabic_to_english(result)
    return result