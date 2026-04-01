import streamlit as st
import feedparser
from deep_translator import GoogleTranslator

st.set_page_config(page_title="외신 속보", layout="wide")

# 🎨 스타일
st.markdown("""
<style>
.main {
    background-color: #0e1117;
}
h1 {
    color: #ffffff;
}
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
        link = entry.link

        news.append((title, summary, link))

    return news

def show_news(title, feed_url):
    st.subheader(title)
    news = load_news(feed_url)

    for t, s, link in news:
        st.markdown(f"""
        <div class="news-card">
            <h4><a href="{link}" target="_blank">{t}</a></h4>
            <p>{s}</p>
        </div>
        """, unsafe_allow_html=True)

with col1:
    show_news("📰 Reuters", feeds["Reuters"])

with col2:
    show_news("📰 BBC", feeds["BBC"])

st.button("🔄 새로고침")
