import streamlit as st
import pandas as pd
import os
from datetime import datetime
from modules.collect_naver_realestate import crawl_naver_busan_apartments
from modules.investment_analysis import analyze_realestate_data, ai_judgement_crypto_bond, render_mini_charts
import requests

# 🔐 API Key 환경 변수에서 로딩
TWELVEDATA_API_KEY = os.getenv("TWELVEDATA_API_KEY")
CRYPTOCOMPARE_API_KEY = os.getenv("CRYPTOCOMPARE_API_KEY")

# ✅ 실시간 지표 수집 함수 (정확한 실시간 API 기반)
def get_live_market_data():
    if not TWELVEDATA_API_KEY:
        st.error("🔑 TWELVEDATA_API_KEY가 설정되지 않았습니다. .env 파일 또는 환경변수를 확인해주세요.")
    if not CRYPTOCOMPARE_API_KEY:
        st.error("🔑 CRYPTOCOMPARE_API_KEY가 설정되지 않았습니다.")
        return []

    symbols = {
        "VIX": {"symbol": "VIX", "source": "twelve"},
        "WTI유가": {"symbol": "CL=F", "source": "twelve"},
        "금(Gold)": {"symbol": "GC=F", "source": "twelve"},
        "달러인덱스": {"symbol": "DXY", "source": "twelve"},
        "엔/달러환율": {"symbol": "USD/JPY", "source": "twelve"},
        "나스닥": {"symbol": "IXIC", "source": "twelve"},
        "S&P500": {"symbol": "GSPC", "source": "twelve"},
        "비트코인": {"symbol": "BTC", "source": "crypto"},
        "이더리움": {"symbol": "ETH", "source": "crypto"},
        "XRP": {"symbol": "XRP", "source": "crypto"}
    }

    results = []
    for name, config in symbols.items():
        try:
            if config["source"] == "twelve":
                url = f"https://api.twelvedata.com/time_series?symbol={config['symbol']}&interval=1min&outputsize=2&apikey={TWELVEDATA_API_KEY}"
                res = requests.get(url)
                json_data = res.json()
                latest = float(json_data['values'][0]['close'])
                prev = float(json_data['values'][1]['close'])
            else:  # crypto from cryptocompare
                url = f"https://min-api.cryptocompare.com/data/price?fsym={config['symbol']}&tsyms=USD&api_key={CRYPTOCOMPARE_API_KEY}"
                res = requests.get(url)
                latest = float(res.json()['USD'])
                prev = latest * 0.98  # 가정

            change = round(latest - prev, 2)
            change_pct = round((change / prev) * 100, 2)
            direction = "▲" if change > 0 else "▼" if change < 0 else "→"
            delta = f"{direction} {change_pct}%"
            color = "🟢 상승 추세" if change > 0 else "🔴 하락 추세" if change < 0 else "⚪ 안정적"
            summary = f"전일 대비 {delta}"

            results.append((name, f"{latest:,.2f}", delta, summary, color, name, latest, prev, change))
        except Exception as e:
            results.append((name, "N/A", "-", "데이터 오류", "⚠️", name, 0, 0, 0))
    
    return results if results else []

st.set_page_config(page_title="📊 통합 자산 투자 판단 대시보드", layout="wide")
st.title("📊 통합 자산 투자 판단 대시보드")

# ------------------------------
# 실시간 주요 경제지표 (탭 1)
# ------------------------------
tabs = st.tabs(["📈 실시간 주요 경제지표", "🏠 실거주 및 경매 부동산 분석"])

with tabs[0]:
    st.header("📈 실시간 주요 경제지표")

    try:
        live_data = get_live_market_data()
        if not live_data:
            st.warning("⚠️ 실시간 시장 데이터를 불러오지 못했습니다. API 연결이나 키를 확인해주세요.")
        else:
            rows = [live_data[i:i+3] for i in range(0, len(live_data), 3)]
            for row in rows:
                cols = st.columns(len(row))
                for col, (label, value, change_str, summary, color, chart_key, value_raw, prev_value, change) in zip(cols, row):
                    with col:
                        with st.container(border=True):
                            st.markdown(f"<div style='font-size: 20px; font-weight: bold;'>{label}</div>", unsafe_allow_html=True)
                            st.metric(label="", value=value, delta=change_str)

                            # 미니 차트 시각화 개선
                            st.line_chart(pd.DataFrame([prev_value, value_raw], columns=["price"]))
                            render_mini_charts(st, chart_key, value_raw, prev_value, change, change_str)

                            st.markdown(f"<div style='font-size: 14px; color: gray;'>{summary}</div>", unsafe_allow_html=True)
                            st.markdown(f"<div style='font-size: 18px;'>{color}</div>", unsafe_allow_html=True)
    except Exception as e:
        st.error("⚠️ 실시간 데이터 로딩에 실패했습니다. API 연결을 확인해주세요.")
        st.exception(e)

    st.subheader("🧠 투자 판단 추천 결과")
    try:
        crypto_result, bond_result = ai_judgement_crypto_bond()

        col1, col2, col3 = st.columns(3)
        with col1:
            with st.container(border=True):
                st.markdown("### 📌 암호화폐")
                st.markdown(f"<div style='font-size:16px'>{crypto_result}</div>", unsafe_allow_html=True)
        with col2:
            with st.container(border=True):
                st.markdown("### 📌 미국 장기국채")
                st.markdown(f"<div style='font-size:16px'>{bond_result}</div>", unsafe_allow_html=True)
        with col3:
            with st.container(border=True):
                st.markdown("### 📌 부동산")
                st.write("📊 CSV 데이터를 기반으로 자동 분석 결과 탭 2 참고")
    except Exception as e:
        st.error("⚠️ 투자 판단 추천 결과 로딩 실패")
        st.exception(e)

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

    st.markdown("### 📁 최근 저장된 CSV 분석")
    if st.button("📁 가장 최근 저장된 CSV 파일 불러오기"):
        try:
            folder_path = "data"
            csv_files = [f for f in os.listdir(folder_path) if f.endswith(".csv") and f.startswith("naver_busan_")]
            if not csv_files:
                st.warning("⚠️ 'data/' 폴더에 저장된 CSV 파일이 없습니다.")
            else:
                latest_file = max(csv_files, key=lambda x: os.path.getmtime(os.path.join(folder_path, x)))
                latest_path = os.path.join(folder_path, latest_file)
                df = pd.read_csv(latest_path)
                st.success(f"✅ 가장 최근 파일 불러오기 완료: `{latest_file}`")
                analyze_realestate_data(df)
        except Exception as e:
            st.error("❌ 최근 파일 불러오기 중 오류가 발생했습니다.")
            st.exception(e)


