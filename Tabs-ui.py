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

st.title("📊 암호화폐 & 미국 국채 & 실거주 부동산 통합 투자 판단 대시보드")

# ---------------- 암호화폐 & 국채 주요 지표 ----------------

st.header("📈 실시간 주요 경제지표")

# 가상 데이터 예시 (실제 데이터는 API로 연결 필요)
data = {
    "XRP": "₩876",
    "BTC 도미넌스": "49.1%",
    "김치프리미엄": "2.3%",
    "공포탐욕지수": 25,
    "미국 10Y 국채금리": "4.25%",
    "S&P 500": "5110.5",
    "나스닥": "16100",
    "달러인덱스": "103.7",
    "WTI 유가": "$82.1",
    "VIX": "13.2",
    "USD/KRW": "₩1,340",
    "JPY/USD": "0.0066"
}

cols = st.columns(4)
metrics = list(data.items())
for i, (label, value) in enumerate(metrics):
    with cols[i % 4]:
        st.metric(label, value)

# ---------------- 투자 판단 추천 ----------------

st.header("🧠 투자 판단 추천 결과")
st.markdown("""
- 📌 **암호화폐**: 중립 (시장 방향성 불확실)
- 📌 **미국 장기국채**: ⏸️ 중립 (특별한 기회 아님)
""")

# ---------------- 부동산 CSV 분석 ----------------

st.header("🏠 실거주 투자용 부동산 분석 (CSV 기반)")

uploaded_file = st.file_uploader("📥 CSV 파일 업로드", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader("📋 데이터 미리보기")
    st.dataframe(df.head())

    st.subheader("🔍 필터 조건 설정")
    max_price = st.slider("총 매매가 상한 (억원)", 1, 10, 5)
    min_jeonse = st.slider("최소 전세가율 (%)", 50, 100, 80)

    df['총매매가억'] = df['총매매가'] / 10000
    filtered = df[(df['총매매가억'] <= max_price) & (df['전세가율'] >= min_jeonse)]

    st.markdown(f"**✅ 조건에 맞는 매물: {len(filtered)}건**")

    def 평가점수(row):
        score = 0
        if row['매물가'] <= row['시세'] * 0.95:
            score += 1
        if row['전세가율'] >= 80:
            score += 1
        if row['임대수익률'] >= 5:
            score += 1
        if row['총매매가'] <= 50000:
            score += 1
        return score

    filtered['적합도점수'] = filtered.apply(평가점수, axis=1)
    filtered['적합도등급'] = filtered['적합도점수'].apply(
        lambda x: '🟢 매우 우수' if x >= 3 else ('🟡 보통' if x == 2 else '🔴 낮음')
    )

    st.subheader("📈 투자 적합도 평가")
    st.dataframe(filtered[['단지명', '매물가', '시세', '전세가율', '임대수익률', '적합도등급']])

    st.info("추후 상세 항목별 분석(공원, 학군 등)도 지원될 예정입니다.")
else:
    st.markdown("👉 CSV 파일을 업로드하면 분석이 시작됩니다. 예시 컬럼: 단지명, 매물가, 시세, 전세가율, 임대수익률, 총매매가")

