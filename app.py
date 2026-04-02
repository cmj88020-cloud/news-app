import streamlit as st
import feedparser
from deep_translator import GoogleTranslator
import re

st.set_page_config(page_title="외신 속보", layout="wide")

# 🎨 네이버 스타일 UI
st.markdown("""
<style>
body {
    background-color: #0e1117;
}
.card {
    display: flex;
    gap: 15px;
    padding: 15px;
    margin-bottom: 12px;
    background-color: #111;
    border-radius: 10px;
    border: 1px solid #222;
    align-items: center;
}
.card:hover {
    background-color: #1a1a1a;
}
.thumb {
    width: 120px;
    height: 80px;
    object-fit: cover;
    border-radius: 6px;
}
.title {
    color: white;
    font-size: 16px;
    font-weight: bold;
}
.summary {
    color: #aaa;
    font-size: 13px;
}
a {
    text-decoration: none;
}
</style>
""", unsafe_allow_html=True)

st.title("📰 외신 속보")

# 카테고리
category = st.selectbox("카테고리", ["전체", "경제", "전쟁", "IT"])

# 새로고침
if st.button("🔄 새로고침"):
    st.cache_data.clear()

feeds = {
    "🌍 World News": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "📰 BBC": "http://feeds.bbci.co.uk/news/world/rss.xml"
}

col1, col2 = st.columns(2)

# 번역
def translate(text):
    try:
        return GoogleTranslator(source='auto', target='ko').translate(text)
    except:
        return text

# 🔥 이미지 추출 (완벽 안정화 버전)
def get_image(entry):
    url = None

    # 1. media_content
    if "media_content" in entry:
        url = entry.media_content[0].get("url")

    # 2. links
    if not url and "links" in entry:
        for link in entry.links:
            if link.get("type", "").startswith("image"):
                url = link.get("href")
                break

    # 3. summary (BBC 대응)
    if not url and "summary" in entry:
        match = re.search(r'<img.*?src="(.*?)"', entry.summary)
        if match:
            url = match.group(1)

    # 4. URL 보정
    if url and url.startswith("//"):
        url = "https:" + url

    # 5. 유효성 체크
    if not url or not url.startswith("http"):
        return None

    return url

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

        # 🔥 이미지 fallback
        img_url = img if img else "https://via.placeholder.com/120x80?text=No+Image"

        st.markdown(f"""
        <a href="{link}" target="_blank">
            <div class="card">
                <img class="thumb" src="{img_url}">
                <div>
                    <div class="title">{t}</div>
                    <div class="summary">{s[:100]}...</div>
                </div>
            </div>
        </a>
        """, unsafe_allow_html=True)

with col1:
    show("🌍 World News", feeds["🌍 World News"])

with col2:
    show("📰 BBC", feeds["📰 BBC"])
