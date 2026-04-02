import streamlit as st
import feedparser
import requests
from deep_translator import GoogleTranslator
from datetime import datetime
from functools import lru_cache

st.set_page_config(page_title="외신 뉴스", layout="wide")

# -------------------------
# 캐싱 (핵심 성능 개선)
# -------------------------
@st.cache_data(ttl=600)
def fetch_rss(url):
    return feedparser.parse(url)

@st.cache_data(ttl=600)
def translate_text(text):
    try:
        return GoogleTranslator(source='auto', target='ko').translate(text)
    except:
        return text

@st.cache_data(ttl=600)
def get_image(url):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return url
    except:
        return None
    return None

# -------------------------
# RSS 목록
# -------------------------
RSS_FEEDS = {
    "경제": "https://rss.nytimes.com/services/xml/rss/nyt/Economy.xml",
    "전쟁": "http://feeds.bbci.co.uk/news/world/rss.xml",
    "IT": "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml"
}

# -------------------------
# UI 상단
# -------------------------
st.title("🌍 외신 뉴스")

col1, col2 = st.columns([3,1])

with col1:
    category = st.selectbox("카테고리 선택", list(RSS_FEEDS.keys()))

with col2:
    if st.button("🔄 새로고침"):
        st.cache_data.clear()

# -------------------------
# 데이터 가져오기
# -------------------------
feed = fetch_rss(RSS_FEEDS[category])

# -------------------------
# 카드 UI 스타일
# -------------------------
st.markdown("""
<style>
.card {
    border-radius: 12px;
    padding: 12px;
    margin-bottom: 15px;
    background-color: #111;
    border: 1px solid #222;
}
.title {
    font-size: 18px;
    font-weight: bold;
}
.summary {
    font-size: 14px;
    color: #aaa;
}
.time {
    font-size: 12px;
    color: #666;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# 뉴스 출력
# -------------------------
for entry in feed.entries[:10]:

    title = entry.title
    summary = entry.summary if "summary" in entry else ""
    link = entry.link

    # 번역 (필요한 것만 → 성능 절약)
    title_ko = translate_text(title)
    summary_ko = translate_text(summary[:150])

    # 시간 처리
    try:
        published = datetime(*entry.published_parsed[:6])
        time_str = published.strftime("%m-%d %H:%M")
    except:
        time_str = ""

    # 이미지 추출 (안정성 개선)
    image_url = None
    if "media_content" in entry:
        image_url = entry.media_content[0]['url']
    elif "links" in entry:
        for link_item in entry.links:
            if "image" in link_item.get("type", ""):
                image_url = link_item.href

    image_url = get_image(image_url) if image_url else None

    # -------------------------
    # 카드 출력
    # -------------------------
    st.markdown('<div class="card">', unsafe_allow_html=True)

    cols = st.columns([1, 3])

    with cols[0]:
        if image_url:
            st.image(image_url, use_container_width=True)
        else:
            st.image("https://via.placeholder.com/150", use_container_width=True)

    with cols[1]:
        st.markdown(f'<div class="title">{title_ko}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="summary">{summary_ko}...</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="time">{time_str}</div>', unsafe_allow_html=True)
        st.link_button("기사 보기", link)

    st.markdown('</div>', unsafe_allow_html=True)
