import streamlit as st
import feedparser
from deep_translator import GoogleTranslator

st.set_page_config(page_title="외신 속보", layout="wide")

# 🎨 스타일
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

# 🔥 안정적으로 되는 RSS (Reuters 대신 NYT 사용)
feeds = {
    "📰 World News (NYT)": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "📰 BBC": "http://feeds.bbci.co.uk/news/world/rss.xml"
}

col1, col2 = st.columns(2)

# 번역 함수
def translate(text):
    try:
        return GoogleTranslator(source='auto', target='ko').translate(text)
    except:
        return text

# 뉴스 불러오기
def load(feed_url):
    news = feedparser.parse(feed_url)
    if not news.entries:
        return []
    return news.entries[:5]

# 뉴스 출력
def show(title, url):
    st.subheader(title)

    news_list = load(url)

    if not news_list:
        st.write("❌ 뉴스 불러오기 실패")
        return

    for entry in news_list:
        t = translate(entry.get("title", ""))
        s = translate(entry.get("summary", entry.get("description", "")))
        link = entry.get("link", "")

        st.markdown(f"""
        <div class="news-card">
            <h4><a href="{link}" target="_blank">{t}</a></h4>
            <p>{s}</p>
        </div>
        """, unsafe_allow_html=True)

with col1:
    show("🌎 World News", feeds["📰 World News (NYT)"])

with col2:
    show("📰 BBC", feeds["📰 BBC"])
