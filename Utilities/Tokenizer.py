import spacy
import nltk
from nltk.tokenize.toktok import ToktokTokenizer

def tokenizerSpacy(tweetText):
    try:
        nlp = spacy.load('es_core_news_sm')
        sentences = tweetText['text']
        doc = nlp(sentences)
        tokens = [token for token in doc]
        print(tokens)
    except Exception as e:
        print(e)

def tokenizerNltk(tweetText):
    try:
        nltk.download('nonbreaking_prefixes')
        nltk.download('perluniprops')
        toktok = ToktokTokenizer()
        toktok.tokenize(tweetText['text'])
        print (",".join(toktok.tokenize(tweetText['text'])))
    except Exception as e:
        print(e)