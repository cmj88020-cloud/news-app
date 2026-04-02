import streamlit as st
import feedparser
from deep_translator import GoogleTranslator

st.set_page_config(page_title="외신 속보", layout="wide")

# 🎨 흑백 스타일
st.markdown("""
<style>
body {
    background-color: #0e1117;
}
.news-card {
    background-color: #111;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 15px;
    border: 1px solid #333;
}
.news-title {
    color: #fff;
    font-weight: bold;
}
.news-summary {
    color: #ccc;
}
</style>
""", unsafe_allow_html=True)

st.title("📰 외신 속보 (한국어 요약)")

# 카테고리 선택
category = st.selectbox(
    "카테고리 선택",
    ["전체", "경제", "전쟁", "IT"]
)

# 새로고침
if st.button("🔄 새로고침"):
    st.cache_data.clear()

feeds = {
    "World News": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "BBC": "http://feeds.bbci.co.uk/news/world/rss.xml"
}

col1, col2 = st.columns(2)

# 번역
def translate(text):
    try:
        return GoogleTranslator(source='auto', target='ko').translate(text)
    except:
        return text

# 썸네일
def get_image(entry):
    if "media_content" in entry:
        return entry.media_content[0]["url"]
    if "links" in entry:
        for link in entry.links:
            if link.get("type", "").startswith("image"):
                return link.get("href")
    return None

# 카테고리 필터
def match_category(text):
    text = text.lower()
    if category == "전체":
        return True
    if category == "경제":
        return any(x in text for x in ["economy", "market", "finance"])
    if category == "전쟁":
        return any(x in text for x in ["war", "military", "attack"])
    if category == "IT":
        return any(x in text for x in ["tech", "ai", "software"])
    return True

# 뉴스 출력
def show(title, url):
    st.subheader(title)
    news = feedparser.parse(url).entries[:8]

    for entry in news:
        title_en = entry.get("title", "")
        summary_en = entry.get("summary", entry.get("description", ""))

        if not match_category(title_en + summary_en):
            continue

        t = translate(title_en)
        s = translate(summary_en)
        link = entry.get("link", "")
        img = get_image(entry)

        if img:
            st.image(img, use_container_width=True)

        st.markdown(f"""
        <div class="news-card">
            <div class="news-title">
                <a href="{link}" target="_blank" style="color:white;">{t}</a>
            </div>
            <div class="news-summary">{s}</div>
        </div>
        """, unsafe_allow_html=True)

with col1:
    show("🌍 World News", feeds["World News"])

with col2:
    show("📰 BBC", feeds["BBC"])
