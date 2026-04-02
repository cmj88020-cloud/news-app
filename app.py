import streamlit as st
import feedparser
from deep_translator import GoogleTranslator

st.set_page_config(page_title="외신 속보", layout="wide")

st.markdown("""
<style>
.news-card {
    background-color: #1c1f26;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)

st.title("🌍 외신 속보 (한국어 요약)")

feeds = {
    "Reuters": "https://www.reutersagency.com/feed/?best-topics=world&post_type=best",
    "BBC": "http://feeds.bbci.co.uk/news/world/rss.xml"
}

col1, col2 = st.columns(2)

def translate(text):
    try:
        return GoogleTranslator(source='auto', target='ko').translate(text)
    except:
        return text

def load(feed_url):
    news = feedparser.parse(feed_url)
    return news.entries[:5]

def show(title, url):
    st.subheader(title)
    for entry in load(url):
        t = translate(entry.title)
        s = translate(entry.summary)
        link = entry.link

        st.markdown(f"""
        <div class="news-card">
            <h4><a href="{link}" target="_blank">{t}</a></h4>
            <p>{s}</p>
        </div>
        """, unsafe_allow_html=True)

with col1:
    show("📰 Reuters", feeds["Reuters"])

with col2:
    show("📰 BBC", feeds["BBC"])
