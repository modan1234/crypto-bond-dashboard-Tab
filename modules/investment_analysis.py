import streamlit as st
import pandas as pd
import random
import matplotlib.pyplot as plt
import numpy as np

# 1. 실거주 부동산 분석
def analyze_realestate_data(df):
    st.subheader("🏢 매물 데이터 요약")
    st.dataframe(df.head(20))

    st.subheader("📊 평형별 전세가 및 월세가 요약")
    grouped = df.groupby("공급면적")[["전세가", "월세가"]].agg(["min", "max", "mean"])
    st.dataframe(grouped)

    st.subheader("💡 AI 자동 투자 판단")
    for i, row in df.iterrows():
        score = (row["전세가"] / (row["공급면적"] * 1000)) * 100
        judgement = "✅ 투자 추천" if score > 0.6 else "❌ 비추천"
        st.markdown(f"• {row['단지명']} ({row['공급면적']}㎡): {judgement}")

# 2. 투자 판단 로직 (암호화폐 & 미국 국채)
def ai_judgement_crypto_bond():
    # 여기서는 임의로 판단 (향후 지표 기반으로 개선 가능)
    crypto_signal = random.choice(["✅ 매수", "❌ 매도", "⏸ 중립"])
    bond_signal = random.choice(["✅ 매수", "❌ 매도", "⏸ 중립"])
    return crypto_signal, bond_signal

# 3. 미니 추세선 차트 (3개월치 랜덤 데이터 시각화)
def render_mini_charts(container, label):
    np.random.seed(hash(label) % 2**32)
    values = np.cumsum(np.random.randn(90)) + 100
    fig, ax = plt.subplots(figsize=(2.5, 1.2))
    ax.plot(values, color="blue", linewidth=1.5)
    ax.axis("off")
    container.pyplot(fig)
