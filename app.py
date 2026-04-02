import streamlit as st
import feedparser
import requests
from deep_translator import GoogleTranslator
from datetime import datetime, timedelta, timezone
import time

st.set_page_config(page_title="외신 뉴스", layout="wide")

# -------------------------
# KST 설정
# -------------------------
KST = timezone(timedelta(hours=9))

# -------------------------
# 자동 새로고침 (5분)
# -------------------------
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

if time.time() - st.session_state.last_refresh > 300:
    st.cache_data.clear()
    st.session_state.last_refresh = time.time()

# -------------------------
# 캐싱
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
# UI
# -------------------------
st.title("🌍 외신 뉴스")

col1, col2 = st.columns([3,1])

with col1:
    category = st.selectbox("카테고리", list(RSS_FEEDS.keys()))

with col2:
    if st.button("🔄 새로고침"):
        st.cache_data.clear()
        st.session_state.last_refresh = time.time()

feed = fetch_rss(RSS_FEEDS[category])

# -------------------------
# 스타일
# -------------------------
st.markdown("""
<style>
.card {border-radius:12px;padding:12px;margin-bottom:15px;background:#111;border:1px solid #222;}
.title {font-size:18px;font-weight:bold;}
.summary {font-size:14px;color:#aaa;}
.time {font-size:12px;color:#666;}
.breaking {color:#ff4b4b;font-weight:bold;}
.core {color:#00c853;font-weight:bold;}
</style>
""", unsafe_allow_html=True)

# -------------------------
# 요약 함수
# -------------------------
def make_core(text):
    t = text.replace("\n", " ")
    return t[:60] + "..." if len(t) > 60 else t

def make_context(text):
    t = text.replace("\n", " ")
    return t[:120] + "..." if len(t) > 120 else t

# -------------------------
# 중요도 계산
# -------------------------
def score_news(entry):
    score = 0
    text = (entry.title + " " + entry.summary).lower()

    keywords = ["war","attack","china","russia","inflation","fed","ai","nvidia","tesla","crisis","oil","rate"]

    for k in keywords:
        if k in text:
            score += 2

    try:
        published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        published_kst = published.astimezone(KST)
        if published_kst > datetime.now(KST) - timedelta(hours=6):
            score += 3
    except:
        pass

    return score

# -------------------------
# TOP5
# -------------------------
entries = feed.entries[:20]
sorted_entries = sorted(entries, key=score_news, reverse=True)
top5 = sorted_entries[:5]

st.subheader("🔥 중요 뉴스 TOP5")

for entry in top5:
    title_ko = translate_text(entry.title)
    summary_ko = translate_text(entry.summary[:150])
    core = make_core(summary_ko)

    st.markdown(f"👉 **{title_ko}**")
    st.markdown(f"<div class='core'>{core}</div>", unsafe_allow_html=True)
    st.markdown("---")

# -------------------------
# 전체 뉴스
# -------------------------
st.subheader("📰 전체 뉴스")

for entry in entries[:10]:

    title = entry.title
    summary = entry.summary if "summary" in entry else ""
    link = entry.link

    title_ko = translate_text(title)
    summary_ko = translate_text(summary[:150])

    core = make_core(summary_ko)
    context = make_context(summary_ko)

    # ✅ KST 시간 변환
    try:
        published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        published_kst = published.astimezone(KST)
        time_str = published_kst.strftime("%m-%d %H:%M")
    except:
        published_kst = None
        time_str = ""

    # 이미지
    image_url = None
    if "media_content" in entry:
        image_url = entry.media_content[0]['url']
    image_url = get_image(image_url) if image_url else None

    st.markdown('<div class="card">', unsafe_allow_html=True)

    # ✅ 속보 (KST 기준)
    if published_kst and published_kst > datetime.now(KST) - timedelta(hours=1):
        st.markdown('<div class="breaking">🔥 속보</div>', unsafe_allow_html=True)

    cols = st.columns([1,3])

    with cols[0]:
        if image_url:
            st.image(image_url, use_container_width=True)
        else:
            st.image("https://via.placeholder.com/150", use_container_width=True)

    with cols[1]:
        st.markdown(f'<div class="title">{title_ko}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="core">👉 {core}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="summary">{context}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="time">{time_str}</div>', unsafe_allow_html=True)
        st.link_button("기사 보기", link)

    st.markdown('</div>', unsafe_allow_html=True)
