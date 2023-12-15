import requests
from bs4 import BeautifulSoup as BS
from textblob import TextBlob
import streamlit as st
import matplotlib.pyplot as plt
import textacy
import re

urll = ['https://www.moneycontrol.com/',
        'https://www.moneycontrol.com/news/business/economy/',
        'https://www.moneycontrol.com/news/business/stocks/',
        'https://www.moneycontrol.com/news/tags/currency.html',
        'https://www.business-standard.com/',
        'https://www.moneycontrol.com/news/business/ipo/',
        'https://www.livemint.com/',
        'https://www.thehindubusinessline.com/']

def fetch_headlines(n):
    response = requests.get('https://hacker-news.firebaseio.com/v0/topstories.json')
    story_ids = response.json()[:n]
    headlines = []

    for story_id in story_ids:
        response = requests.get(f'https://hacker-news.firebaseio.com/v0/item/{story_id}.json')
        story = response.json()
        headlines.append(story['title'])

    for url in urll:
        webpage = requests.get(url)

        trav = BS(webpage.content, "html.parser")

        #For serial number
        
        M = 1

        for link in trav.find_all('a'):

            # PASTE THE CLASS TYPE THAT WE GET
            # FROM THE ABOVE CODE IN THIS AND
            # SET THE LIMIT GREATER THAN 35

            if (str(type(link.string)) == "<class 'bs4.element.NavigableString'>"

            and len(link.string) > 35):

                words = link.string.split()
                if (len(words)<6):
                    continue

                headlines.append(link.string)

                M += 1

    return headlines

def analyze_sentiment(headlines):
    positive = 0
    negative = 0
    neutral = 0

    for headline in headlines:
        analysis = TextBlob(headline)
        if analysis.sentiment.polarity > 0:
            positive += 1
        elif analysis.sentiment.polarity < 0:
            negative += 1
        else:
            neutral += 1

    return positive, negative, neutral

def extract_keyphrases(text, num):
    en = textacy.load_spacy_lang("en_core_web_sm", disable=("parser",))
    doc = textacy.make_spacy_doc(text, lang=en)
    keyphrases = textacy.extract.keyterms.textrank(doc, normalize="lemma", topn=20)[:num]
    
    return keyphrases

def main():
    st.title("Financial News Sentiment Analysis")

    num_headlines = st.slider("Number of headlines", 1, 100, 50)
    headlines = fetch_headlines(num_headlines)

    st.subheader("Headlines")
    for headline in headlines:
        st.write(headline)

    positive, negative, neutral = analyze_sentiment(headlines)

    st.subheader("Sentiment Analysis")
    fig, ax = plt.subplots()
    ax.bar(["Positive", "Negative", "Neutral"], [positive, negative, neutral])
    st.pyplot(fig)

    st.subheader("Keyphrase Extraction")
    text = ". ".join(headlines)
    keyphrases = extract_keyphrases(text, 20)
    for phrase, score in keyphrases:
        st.write(re.sub(r'[^a-zA-Z0-9\s]', '', phrase), score)

if __name__ == "__main__":
    main()
