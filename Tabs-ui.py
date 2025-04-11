import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates  # 추가됨
from datetime import datetime, timedelta

st.set_page_config(layout="wide")
st.markdown("""
    <style>
    h1, h2, h3, h4, h5, h6 {
        font-weight: 700;
        margin-top: 1rem;
    }
    .element-container {
        padding: 1rem;
    }
    .stMetric {
        font-size: 1.2rem;
    }
    .stMarkdown p {
        font-size: 1.1rem;
    }
    .stDataFrame, .stTable {
        font-size: 0.9rem;
    }
    .background-container {
        position: fixed;
        top: 10%;
        right: 2%;
        width: 180px;
        opacity: 0.3;
        z-index: -1;
    }
    </style>
    <div class="background-container">
        <img src="https://files.oaiusercontent.com/file_00000000dbc861f69a9e2a1bbe407dd2" width="100%">
    </div>
""", unsafe_allow_html=True)

탭1, 탭2 = st.tabs(["📊 투자 판단 대시보드", "🧠 추가 분석 보기"])

def price_with_trend(symbol, price):
    previous = st.session_state.get(f"prev_{symbol}")
    st.session_state[f"prev_{symbol}"] = price
    if previous is None:
        return f"₩{price:,.0f} 🟡■"
    if price > previous:
        return f"₩{price:,.0f} 🟢▲"
    elif price < previous:
        return f"₩{price:,.0f} 🔴▼"
    else:
        return f"₩{price:,.0f} 🟡■"

@st.cache_data(ttl=60)
def get_naver_price(code):
    try:
        url = f"https://finance.naver.com/item/main.nhn?code={code}"
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")
        price_tag = soup.select_one("p.no_today span.blind")
        return float(price_tag.text.replace(',', '')) if price_tag else None
    except:
        return None

@st.cache_data(ttl=60)
def get_kimpga_history():
    try:
        url = "https://kimpga.com/api/chart/"
        res = requests.get(url)
        json_data = res.json()
        data = pd.DataFrame(json_data)
        data["date"] = pd.to_datetime(data["date"])
        data["kimp"] = pd.to_numeric(data["kimp"], errors="coerce")
        data["dominance"] = pd.to_numeric(data["dominance"], errors="coerce")
        data.dropna(subset=["kimp", "dominance"], inplace=True)
        data.sort_values("date", inplace=True)
        recent_data = data.tail(7)
        return recent_data
    except:
        return None

@st.cache_data(ttl=60)
def get_kimpga_data():
    try:
        url = "https://kimpga.com/"
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")
        items = soup.select("div.flex.flex-wrap div.text-xs.text-gray-500")
        data = {}
        for item in items:
            text = item.get_text()
            if "김치프리미엄" in text:
                data['kimp'] = item.find_next("div").get_text()
            if "도미넌스" in text:
                data['dominance'] = item.find_next("div").get_text()
        return data
    except:
        return {"kimp": None, "dominance": None}

@st.cache_data(ttl=60)
def get_fear_greed_index():
    try:
        url = "https://datalab.upbit.com/"
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")
        index_div = soup.find("div", string="공포탐욕지수")
        if index_div:
            value_div = index_div.find_next("div")
            return value_div.get_text(strip=True)
        return "N/A"
    except:
        return "N/A"

with 탭1:
    st.image("https://files.oaiusercontent.com/file_00000000dbc861f69a9e2a1bbe407dd2", width=180)
    st.markdown("## 📈 암호화폐(XRP) & 미국 국채(10Y) 투자판단 대시보드")
    st.markdown("### 🧭 실시간 주요 지표 (1분마다 자동 갱신)")

    코드들 = {
        "xrp": ("538840", "🚀 XRP 현재가"),
        "bond": ("267440", "📉 미국 10Y 금리 ETF"),
        "dxy": ("195930", "💵 달러인덱스 ETF"),
        "oil": ("261220", "🛢️ WTI 유가 ETF"),
        "nasdaq": ("133690", "📈 나스닥 ETF"),
        "vix": ("276970", "🧊 VIX ETF"),
        "sp500": ("148070", "📊 S&P 500 ETF"),
        "usdkrw": ("261240", "💱 원/달러 ETF"),
        "usdjpy": ("276990", "💴 엔/달러 ETF")
    }

    cols = st.columns(5)
    prices = {}

    for i, (symbol, (code, label)) in enumerate(코드들.items()):
        price = get_naver_price(code)
        prices[symbol] = price
        with cols[i % 5]:
            st.metric(label, price_with_trend(symbol, price) if price else "N/A")

    kimp_data = get_kimpga_data()
    fear_greed = get_fear_greed_index()

    col11, col12 = st.columns(2)
    with col11:
        st.metric("🇰🇷 김치프리미엄", kimp_data['kimp'] or "N/A")

    with col12:
        st.metric("🔗 BTC 도미넌스", kimp_data['dominance'] or "N/A")

    st.markdown("### 🧠 공포·탐욕 지수")
    if fear_greed != "N/A":
        try:
            fg_value = int(''.join(filter(str.isdigit, fear_greed)))
            if fg_value <= 25:
                st.markdown(f"<span style='color:red;font-size:24px;font-weight:bold;'>📉 공포 ({fg_value})</span>", unsafe_allow_html=True)
            elif fg_value <= 50:
                st.markdown(f"<span style='color:orange;font-size:24px;font-weight:bold;'>😐 중립 ({fg_value})</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"<span style='color:green;font-size:24px;font-weight:bold;'>📈 탐욕 ({fg_value})</span>", unsafe_allow_html=True)
        except:
            st.write(fear_greed)
    else:
        st.write("N/A")

    st.markdown("---")
    st.markdown("### 🔎 지금 투자해도 될까?")

    try:
        xrp = prices.get("xrp")
        bond = prices.get("bond")
        if xrp and bond:
            if xrp < 500 and bond > 11000:
                st.success("✅ **매수 추천**: XRP 저점 + 금리 고점으로 판단됩니다.")
            elif xrp > 1000 and bond < 10000:
                st.error("⚠️ **매도 추천**: XRP 고점 + 금리 저점으로 위험합니다.")
            else:
                st.warning("🤔 **중립 판단**: 아직 명확한 투자 신호는 없습니다.")
        else:
            st.markdown("❌ 데이터를 불러오거나 처리하는 중 오류가 발생했습니다.")
    except Exception as e:
        st.markdown(f"❌ 오류 발생: {str(e)}")

    st.markdown("---")
    st.markdown("ⓒ 2025. 투자참고용 대시보드 by modan1234")

with 탭2:
    st.markdown("## 🧠 추가 분석")
    st.markdown("### 김치프리미엄 & 도미넌스 추이 (최근 7일)")

    data = get_kimpga_history()
    if data is not None:
        try:
            fig, ax = plt.subplots(figsize=(8, 3))
            ax.plot(data["date"], data["kimp"], label="김치프리미엄", color="red", marker='o')
            ax.plot(data["date"], data["dominance"], label="도미넌스", color="blue", marker='o')
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
            fig.autofmt_xdate()
            ax.set_ylabel("%")
            ax.set_title("7일 추이 그래프")
            ax.legend()
            ax.grid(True)
            st.pyplot(fig)
        except Exception as e:
            st.error(f"그래프 표시 중 오류 발생: {str(e)}")
    else:
        st.warning("❗ 추이 데이터를 불러올 수 없습니다.")

    st.markdown("### 📉 MACD & RSI 기술적 분석 기능 준비 중입니다.")
