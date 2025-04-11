import streamlit as st
import pandas as pd
import os
from datetime import datetime
from modules.collect_naver_realestate import crawl_naver_busan_apartments
from modules.investment_analysis import analyze_realestate_data, ai_judgement_crypto_bond, render_mini_charts

st.set_page_config(page_title="📊 통합 자산 투자 판단 대시보드", layout="wide")
st.title("📊 통합 자산 투자 판단 대시보드")

# ------------------------------
# 실시간 주요 경제지표 (탭 1)
# ------------------------------
tabs = st.tabs(["📈 실시간 주요 경제지표", "🏠 실거주 및 경매 부동산 분석"])

with tabs[0]:
    st.header("📈 실시간 주요 경제지표")

    col1, col2, col3, col4 = st.columns(4)
    col1.markdown("<div style='font-size: 20px; font-weight: bold;'>XRP</div>", unsafe_allow_html=True)
    col1.metric(label="", value="₩876")
    render_mini_charts(col1, 'XRP')

    col2.markdown("<div style='font-size: 20px; font-weight: bold;'>미국 10Y 국채금리</div>", unsafe_allow_html=True)
    col2.metric(label="", value="4.25%")
    render_mini_charts(col2, '10Y')

    col3.markdown("<div style='font-size: 20px; font-weight: bold;'>WTI 유가</div>", unsafe_allow_html=True)
    col3.metric(label="", value="$82.1")
    render_mini_charts(col3, 'WTI')

    col4.markdown("<div style='font-size: 20px; font-weight: bold;'>BTC 도미넌스</div>", unsafe_allow_html=True)
    col4.metric(label="", value="49.1%")
    render_mini_charts(col4, 'BTC_DOM')

    col5, col6, col7, col8 = st.columns(4)
    col5.markdown("<div style='font-size: 20px; font-weight: bold;'>S&P 500</div>", unsafe_allow_html=True)
    col5.metric(label="", value="5110.5")
    render_mini_charts(col5, 'SP500')

    col6.markdown("<div style='font-size: 20px; font-weight: bold;'>VIX</div>", unsafe_allow_html=True)
    col6.metric(label="", value="13.2")
    render_mini_charts(col6, 'VIX')

    col7.markdown("<div style='font-size: 20px; font-weight: bold;'>김치프리미엄</div>", unsafe_allow_html=True)
    col7.metric(label="", value="2.3%")
    render_mini_charts(col7, 'Kimchi')

    col8.markdown("<div style='font-size: 20px; font-weight: bold;'>나스닥</div>", unsafe_allow_html=True)
    col8.metric(label="", value="16100")
    render_mini_charts(col8, 'NASDAQ')

    col9, col10, col11, col12 = st.columns(4)
    col9.markdown("<div style='font-size: 20px; font-weight: bold;'>USD/KRW</div>", unsafe_allow_html=True)
    col9.metric(label="", value="₩1,340")
    render_mini_charts(col9, 'USD_KRW')

    col10.markdown("<div style='font-size: 20px; font-weight: bold;'>공포탐욕지수</div>", unsafe_allow_html=True)
    col10.metric(label="", value="25")
    render_mini_charts(col10, 'FearGreed')

    col11.markdown("<div style='font-size: 20px; font-weight: bold;'>달러인덱스</div>", unsafe_allow_html=True)
    col11.metric(label="", value="103.7")
    render_mini_charts(col11, 'DXY')

    col12.markdown("<div style='font-size: 20px; font-weight: bold;'>엔/달러 환율</div>", unsafe_allow_html=True)
    col12.metric(label="", value="¥151.5")
    render_mini_charts(col12, 'JPY_USD')

    st.subheader("🧠 투자 판단 추천 결과")
    crypto_result, bond_result = ai_judgement_crypto_bond()
    st.markdown(f"""
    📌 **암호화폐**: {crypto_result}  
    📌 **미국 장기국채**: {bond_result}  
    📌 **부동산 투자 판단**: 📊 CSV 데이터를 기반으로 자동 분석 결과 탭 2 참고
    """)

# ------------------------------
# 실거주 부동산 분석 (탭 2)
# ------------------------------
with tabs[1]:
    st.subheader("🏠 실거주 투자용 부동산 분석 (CSV 기반)")

    st.markdown("""
    ### 📥 CSV 파일 업로드
    👉 CSV 파일을 업로드하면 분석이 시작됩니다. 예시 컬럼: 단지명, 공급면적, 전용면적, 전세가, 월세가, 전세가율, 임대수익률, 총매매가 등
    ※ 중복 매물은 자동 제거되며, 공급면적 35평 이하만 분석에 포함됩니다.
    ※ 전용면적/공급면적 구분 표시됩니다.
    ※ 단지별 평형별 최고/최저 전세가, 월세가 분석 포함됩니다.
    ※ 급매 여부도 실거래 최저가 기준 자동 판단됩니다.
    ※ 최근 5년 실거래 변동사항을 작고 간결한 그래프로 표시합니다.
    ※ 투자 판단은 데이터 기반으로 AI가 자동 권유합니다.
    """)
    uploaded_file = st.file_uploader("", type="csv")

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        analyze_realestate_data(df)

    st.divider()
    st.markdown("### 📥 부산 매물 최신 데이터 수집하기")
    if st.button("📡 네이버 부동산에서 자동 수집 시작"):
        with st.spinner("데이터 수집 중입니다. 잠시만 기다려주세요..."):
            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = f"data/naver_busan_{now}.csv"
            os.makedirs("data", exist_ok=True)
            df = crawl_naver_busan_apartments()
            df.to_csv(save_path, index=False)
            st.success("✅ 수집 완료! 분석을 시작합니다.")
            analyze_realestate_data(df)
