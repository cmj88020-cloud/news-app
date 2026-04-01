import streamlit as st
import feedparser
from deep_translator import GoogleTranslator

st.set_page_config(page_title="외신 속보 요약", layout="wide")

st.title("🌍 외신 속보 (한국어 요약)")

feeds = {
    "Reuters": "http://feeds.reuters.com/reuters/worldNews",
    "BBC": "http://feeds.bbci.co.uk/news/world/rss.xml"
}

col1, col2 = st.columns(2)

def translate_text(text):
    try:
        return GoogleTranslator(source='auto', target='ko').translate(text)
    except:
        return text

def load_news(feed_url):
    news = []
    feed = feedparser.parse(feed_url)

    for entry in feed.entries[:5]:
        title = translate_text(entry.title)
        summary = translate_text(entry.summary)

        news.append((title, summary))

    return news

with col1:
    st.subheader("📰 Reuters")
    news = load_news(feeds["Reuters"])
    for title, summary in news:
        st.markdown(f"### {title}")
        st.write(summary)
        st.markdown("---")

with col2:
    st.subheader("📰 BBC")
    news = load_news(feeds["BBC"])
    for title, summary in news:
        st.markdown(f"### {title}")
        st.write(summary)
        st.markdown("---")

st.button("🔄 새로고침")
