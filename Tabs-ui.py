import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
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
        return {}

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

# 실행 명령 예시
# streamlit run tabs-ui.py --server.enableCORS false

