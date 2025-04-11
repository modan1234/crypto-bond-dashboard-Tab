import streamlit as st
import pandas as pd
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import numpy as np

st.set_page_config(layout="wide")

# 탭 UI
탭1, 탭2 = st.tabs(["📊 투자 판단 대시보드", "🧠 추가 분석 보기"])

with 탭1:
    # 제목
    st.markdown("## 📈 암호화폐(XRP) & 미국 국채(10Y) 투자판단 대시보드")

    # --- 주요 실시간 지표 숫자 표시 ---
    st.markdown("### 🧭 실시간 주요 지표")

    # 지표 불러오는 함수
    def get_latest_price(ticker):
        try:
            data = yf.download(ticker, period="5d", interval="1h")
            return data["Close"].dropna().iloc[-1]
        except:
            return None

    # 김치프리미엄 & 도미넌스 크롤링
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

    # 공포탐욕지수 크롤링 (업비트 데이터랩)
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

    # 지표 나열 (모바일 대응: 최대 2~3개씩)
    col1, col2 = st.columns(2)
    with col1:
        xrp = get_latest_price("XRP-USD")
        st.metric("🚀 XRP 현재가", f"${xrp:.3f}" if xrp else "N/A")

    with col2:
        bond = get_latest_price("^TNX")
        bond_display = bond / 100 if bond else None
        st.metric("📉 미국 10Y 금리", f"{bond_display:.2f}%" if bond_display else "N/A")

    col3, col4 = st.columns(2)
    with col3:
        dxy = get_latest_price("DX-Y.NYB")
        st.metric("💵 달러인덱스", f"{dxy:.2f}" if dxy else "N/A")

    with col4:
        oil = get_latest_price("CL=F")
        st.metric("🛢️ WTI 유가", f"${oil:.2f}" if oil else "N/A")

    col5, col6 = st.columns(2)
    with col5:
        nasdaq = get_latest_price("^IXIC")
        st.metric("📈 나스닥", f"{nasdaq:,.0f}" if nasdaq else "N/A")

    with col6:
        vix = get_latest_price("^VIX")
        st.metric("🧊 VIX 변동성", f"{vix:.2f}" if vix else "N/A")

    col7, col8 = st.columns(2)
    with col7:
        sp500 = get_latest_price("^GSPC")
        st.metric("📊 S&P 500", f"{sp500:,.0f}" if sp500 else "N/A")

    with col8:
        usdkrw = get_latest_price("KRW=X")
        st.metric("💱 원/달러", f"{usdkrw:,.2f}" if usdkrw else "N/A")

    col9, col10 = st.columns(2)
    with col9:
        usdjpy = get_latest_price("JPY=X")
        st.metric("💴 엔/달러", f"{usdjpy:,.2f}" if usdjpy else "N/A")

    kimp_data = get_kimpga_data()
    fear_greed = get_fear_greed_index()

    col11, col12 = st.columns(2)
    with col11:
        st.metric("🇰🇷 김치프리미엄", kimp_data['kimp'] or "N/A")

    with col12:
        st.metric("🔗 BTC 도미넌스", kimp_data['dominance'] or "N/A")

    # 공포탐욕지수 색상 구분
    st.markdown("### 🧠 공포·탐욕 지수")
    if fear_greed != "N/A":
        try:
            fg_value = int(''.join(filter(str.isdigit, fear_greed)))
            if fg_value <= 25:
                st.markdown(f"<span style='color:red;font-size:24px;font-weight:bold;'>공포 ({fg_value})</span>", unsafe_allow_html=True)
            elif fg_value <= 50:
                st.markdown(f"<span style='color:orange;font-size:24px;font-weight:bold;'>중립 ({fg_value})</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"<span style='color:green;font-size:24px;font-weight:bold;'>탐욕 ({fg_value})</span>", unsafe_allow_html=True)
        except:
            st.write(fear_greed)
    else:
        st.write("N/A")

    # --- 투자 판단 로직 ---
    st.markdown("---")
    st.markdown("### 🔎 현재 지표로 본 투자 판단")

    try:
        if xrp and bond_display:
            if xrp < 0.5 and bond_display > 4:
                st.markdown("""
                💡 **추천 판단:** 🔵 매수 (XRP 저점 + 금리 고점)
                - **AI 추천이유**: XRP가 저평가되어 있고, 국채 금리가 높아 추후 금리 인하 시 자산 가격 반등 가능성이 높습니다.
                """)
            elif xrp > 1.0 and bond_display < 3:
                st.markdown("""
                💡 **추천 판단:** 🔴 매도 (XRP 고점 + 금리 저점)
                - **AI 추천이유**: XRP가 고평가 영역에 있으며, 금리가 낮은 상황에서는 향후 긴축 가능성으로 인해 자산 가격 하락 우려가 있습니다.
                """)
            else:
                st.markdown("""
                💡 **추천 판단:** 🟡 중립 (더 많은 데이터 필요)
                - **AI 추천이유**: 현재 가격과 금리가 모두 애매한 수준으로, 명확한 매수/매도 신호가 부족합니다.
                """)
        else:
            st.markdown("❌ 데이터를 불러오거나 처리하는 중 오류가 발생했습니다.")
    except Exception as e:
        st.markdown(f"❌ 오류 발생: {str(e)}")

    st.markdown("---")
    st.markdown("ⓒ 2025. 투자참고용 대시보드 by modan1234")

with 탭2:
    st.markdown("## 🧠 추가 분석")

    # RSI 기술적 분석
    st.markdown("### 📊 XRP RSI 분석")
    rsi_data = yf.download("XRP-USD", period="1mo", interval="1d")
    delta = rsi_data["Close"].diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    st.line_chart(rsi, height=200)

    # AI 투자 판단 예고
    st.markdown("### 🤖 AI 투자판단 학습기능 (예정)")
    st.info("XRP와 금리, 시장 지표를 바탕으로 머신러닝 모델이 향후 수익률을 예측합니다. 추후 XGBoost 기반 모델 탑재 예정입니다.")

    # 포트폴리오 시뮬레이션
    st.markdown("### 📈 자산별 포트폴리오 시뮬레이션 (예시)")
    st.write("XRP 40%, 미국채 60% 포트폴리오 수익률")
    crypto_data = yf.download("XRP-USD", start="2022-01-01")
    bond_data = yf.download("IEF", start="2022-01-01")
    crypto_returns = crypto_data["Close"].pct_change().fillna(0)
    bond_returns = bond_data["Close"].pct_change().fillna(0)
    portfolio_returns = crypto_returns * 0.4 + bond_returns * 0.6
    portfolio_cumulative = (1 + portfolio_returns).cumprod()
    st.line_chart(portfolio_cumulative, height=200)
