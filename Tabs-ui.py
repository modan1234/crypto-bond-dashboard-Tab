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

def price_with_trend(symbol, price, currency='$'):
    if symbol == "XRP":
        currency = '₩'
    previous = st.session_state.get(f"prev_{symbol}")
    st.session_state[f"prev_{symbol}"] = price
    if previous is None:
        return f"{currency}{price:,.0f} 🟡■"
    if price > previous:
        return f"{currency}{price:,.0f} 🟢▲"
    elif price < previous:
        return f"{currency}{price:,.0f} 🔴▼"
    else:
        return f"{currency}{price:,.0f} 🟡■"

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
        url = "https://api.alternative.me/fng/"
        res = requests.get(url)
        data = res.json()
        return data['data'][0]['value']
    except:
        return "N/A"

def evaluate_investment(xrp_price, kimp, dominance, fear_greed):
    if xrp_price is None or kimp is None or dominance is None or fear_greed is None:
        return "📌 데이터 부족으로 판단할 수 없습니다."
    try:
        kimp = float(kimp.replace('%','').replace('+','').replace('−','-'))
        dominance = float(dominance.replace('%','').replace('+','').replace('−','-'))
        fear_greed = int(fear_greed)

        if kimp < 0 and fear_greed < 30 and dominance > 50:
            return "✅ **매수 추천**: 저평가 + 시장 공포 + BTC 강세"
        elif kimp > 2 and fear_greed > 70 and dominance < 48:
            return "🚨 **매도 추천**: 고평가 + 시장 과열 + BTC 약세"
        else:
            return "⏸️ **중립**: 뚜렷한 신호 없음, 관망 권장"
    except:
        return "❓ 데이터 처리 오류"

def evaluate_bond_investment(interest_rate, usdkrw, dxy):
    if None in (interest_rate, usdkrw, dxy):
        return "📌 데이터 부족으로 판단할 수 없습니다."
    try:
        if interest_rate < 4.0 and usdkrw < 1350 and dxy < 104:
            return "✅ **매수 추천**: 금리 안정 + 엔화 강세 환경"
        elif interest_rate > 4.4 and dxy > 106:
            return "🚨 **매도 권고**: 고금리 + 강달러 환경"
        else:
            return "⏸️ **중립**: 특별한 기회 아님"
    except:
        return "❓ 데이터 처리 오류"

# 탭 구성
tab1, tab2 = st.tabs(["📊 암호화폐 판단", "💵 미국 국채 판단"])

with tab1:
    st.subheader("📊 투자 판단 대시보드")
    kimp_data = get_kimpga_data()
    xrp_price = get_naver_price("KR7035720002")
    fg_index = get_fear_greed_index()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🇰🇷 김치프리미엄", kimp_data.get("kimp", "N/A"))
    with col2:
        st.metric("🔗 BTC 도미넌스", kimp_data.get("dominance", "N/A"))
    with col3:
        st.metric("😨 공포·탐욕 지수", fg_index)

    st.markdown("""
    #### 🧠 투자 판단 추천 결과
    """)
    st.success(evaluate_investment(xrp_price, kimp_data.get("kimp"), kimp_data.get("dominance"), fg_index))

    st.markdown("""
    #### 📈 최근 7일간 김치프리미엄 및 비트코인 도미넌스 추이
    - 투자 분위기와 심리를 종합적으로 판단하는 데 참고하세요.
    """)

    kimpga_history = get_kimpga_history()
    if kimpga_history is not None and not kimpga_history.empty:
        fig, ax1 = plt.subplots(figsize=(10, 4))
        ax1.plot(kimpga_history['date'], kimpga_history['kimp'], color='red', marker='o', label='김치프리미엄 (%)')
        ax1.set_ylabel('김치프리미엄 (%)', color='red')
        ax1.tick_params(axis='y', labelcolor='red')
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))

        ax2 = ax1.twinx()
        ax2.plot(kimpga_history['date'], kimpga_history['dominance'], color='blue', marker='o', label='BTC 도미넌스 (%)')
        ax2.set_ylabel('BTC 도미넌스 (%)', color='blue')
        ax2.tick_params(axis='y', labelcolor='blue')

        fig.autofmt_xdate()
        plt.title("최근 7일간 김치프리미엄 및 비트코인 도미넌스 추이")
        st.pyplot(fig)
    else:
        st.warning("Kimpga 데이터 로딩에 실패했습니다.")

with tab2:
    st.subheader("💵 미국 장기국채 투자 판단")
    # 샘플 데이터 (추후 실시간 API로 교체)
    bond_rate = 4.25
    usdkrw = 1340
    dxy = 103.7

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🇺🇸 美 10년 금리", f"{bond_rate:.2f}%")
    with col2:
        st.metric("💱 원/달러 환율", f"₩{usdkrw:,.0f}")
    with col3:
        st.metric("📊 달러인덱스(DXY)", f"{dxy:.1f}")

    st.markdown("""
    #### 🧠 투자 판단 추천 결과
    """)
    st.success(evaluate_bond_investment(bond_rate, usdkrw, dxy))

