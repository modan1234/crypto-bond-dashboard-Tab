import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

st.set_page_config(layout="wide")

# 탭 UI
탭1, 탭2 = st.tabs(["📊 투자 판단 대시보드", "🧠 추가 분석 보기"])

# 가격 변화 비교 함수
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
    st.markdown("## 📈 암호화폐(XRP) & 미국 국채(10Y) 투자판단 대시보드")
    st.markdown("### 🧭 실시간 주요 지표 (1분마다 자동 갱신)")

    col1, col2 = st.columns(2)
    with col1:
        xrp = get_naver_price("538840")
        st.metric("🚀 XRP 현재가", price_with_trend("xrp", xrp) if xrp else "N/A")

    with col2:
        bond = get_naver_price("267440")
        st.metric("📉 미국 10Y 금리 ETF", price_with_trend("bond", bond) if bond else "N/A")

    col3, col4 = st.columns(2)
    with col3:
        dxy = get_naver_price("195930")
        st.metric("💵 달러인덱스 ETF", price_with_trend("dxy", dxy) if dxy else "N/A")

    with col4:
        oil = get_naver_price("261220")
        st.metric("🛢️ WTI 유가 ETF", price_with_trend("oil", oil) if oil else "N/A")

    col5, col6 = st.columns(2)
    with col5:
        nasdaq = get_naver_price("133690")
        st.metric("📈 나스닥 ETF", price_with_trend("nasdaq", nasdaq) if nasdaq else "N/A")

    with col6:
        vix = get_naver_price("276970")
        st.metric("🧊 VIX ETF", price_with_trend("vix", vix) if vix else "N/A")

    col7, col8 = st.columns(2)
    with col7:
        sp500 = get_naver_price("148070")
        st.metric("📊 S&P 500 ETF", price_with_trend("sp500", sp500) if sp500 else "N/A")

    with col8:
        usdkrw = get_naver_price("261240")
        st.metric("💱 원/달러 ETF", price_with_trend("usdkrw", usdkrw) if usdkrw else "N/A")

    col9, col10 = st.columns(2)
    with col9:
        usdjpy = get_naver_price("276990")
        st.metric("💴 엔/달러 ETF", price_with_trend("usdjpy", usdjpy) if usdjpy else "N/A")

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
            fig, ax = plt.subplots(figsize=(6, 3))
            ax.plot(data["date"], data["kimp"], label="김치프리미엄", color="red", marker='o')
            ax.plot(data["date"], data["dominance"], label="도미넌스", color="blue", marker='o')
            ax.set_ylabel("%")
            ax.set_title("7일 추이 그래프")
            ax.legend()
            ax.grid(True)
            plt.xticks(rotation=45)
            st.pyplot(fig)
        except Exception as e:
            st.error(f"그래프 표시 중 오류 발생: {str(e)}")
    else:
        st.warning("❗ 추이 데이터를 불러올 수 없습니다.")

    st.markdown("### 📉 MACD & RSI 기술적 분석 기능 준비 중입니다.")

