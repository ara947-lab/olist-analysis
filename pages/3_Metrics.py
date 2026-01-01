import streamlit as st


import streamlit as st
import pandas as pd
import plotly.express as px

st.title("📉 행동 지표 비교")

seller_6m = pd.read_csv("data/seller_6m.csv")

metrics_mean = (
    seller_6m
    .groupby("risk_stage")[["orders_6m", "active_days_6m"]]
    .mean()
    .reset_index()
)

fig = px.bar(
    metrics_mean,
    x="risk_stage",
    y=["orders_6m", "active_days_6m"],
    barmode="group",
    title="Risk Stage별 평균 주문 수 / 활동 일수"
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("""
### 해석
- Risk Stage가 나빠질수록  
👉 **주문 수와 활동 일수가 급격히 감소**
""")
