# =========================
# Olist Seller Risk Dashboard
# =========================

import os
import pandas as pd
import streamlit as st
import altair as alt

# -------------------------
# Page Config
# -------------------------
st.set_page_config(
    page_title="Olist Seller Risk Dashboard",
    layout="wide"
)

# -------------------------
# Data Load
# -------------------------
@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, "data", "seller_6m_features.csv")
    df = pd.read_csv(csv_path)

    numeric_cols = ["orders_6m", "active_days_6m", "revenue_6m", "avg_review_6m"]
    for c in numeric_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    return df

df = load_data()

# -------------------------
# Risk 정의 (CSV 기준)
# -------------------------
risk_mask = df["risk_group"] == "risk"

# -------------------------
# KPI
# -------------------------
total_seller = df["seller_id"].nunique()
risk_seller = df.loc[risk_mask, "seller_id"].nunique()
risk_ratio = risk_seller / total_seller * 100

avg_orders_all = df["orders_6m"].mean()
avg_orders_risk = df.loc[risk_mask, "orders_6m"].mean()

avg_active_all = df["active_days_6m"].mean()
avg_active_risk = df.loc[risk_mask, "active_days_6m"].mean()

# -------------------------
# Title
# -------------------------
st.title("🛒 Olist Seller Risk Dashboard")
st.caption("초기 6개월 행동 기반 판매자 이탈 조기 경보")

# -------------------------
# KPI View
# -------------------------
c1, c2, c3, c4 = st.columns(4)

c1.metric("전체 판매자 수", f"{total_seller:,}")
c2.metric("이탈 위험 판매자 비율", f"{risk_ratio:.1f}%")

c3.metric(
    "평균 주문 수 (전체)",
    f"{avg_orders_all:.1f}",
    delta=f"{avg_orders_all - avg_orders_risk:.1f} (위험군 대비)"
)

c4.metric(
    "평균 활동 일수 (전체)",
    f"{avg_active_all:.1f}",
    delta=f"{avg_active_all - avg_active_risk:.1f} (위험군 대비)"
)

st.divider()

st.info("📌 이탈은 리뷰 이전에 **주문·활동 감소로 먼저 시작된다**")

# -------------------------
# Risk Stage 분포 (위험군 내부)
# -------------------------
st.subheader("이탈 위험 판매자 Risk Stage 분포")

stage_order = ["almost_churn", "low_active", "recoverable"]

stage_cnt = (
    df.loc[risk_mask, "risk_stage"]
    .value_counts()
    .reindex(stage_order, fill_value=0)
    .reset_index()
)

stage_cnt.columns = ["risk_stage", "count"]

# Altair 타입 명시
stage_cnt["risk_stage"] = stage_cnt["risk_stage"].astype(str)
stage_cnt["count"] = stage_cnt["count"].astype(int)

chart = (
    alt.Chart(stage_cnt)
    .mark_bar()
    .encode(
        x=alt.X("risk_stage:N", sort=stage_order, title=None),
        y=alt.Y("count:Q", title="판매자 수"),
        tooltip=["risk_stage", "count"]
    )
    .properties(height=300)
)

st.altair_chart(chart, use_container_width=True)

# -------------------------
# Stage별 행동 지표
# -------------------------
st.subheader("Risk Stage별 평균 행동 지표")

agg = (
    df.groupby("risk_stage", as_index=False)
    .agg(
        orders_6m=("orders_6m", "mean"),
        active_days_6m=("active_days_6m", "mean"),
        sellers=("seller_id", "nunique")
    )
)

st.dataframe(agg, use_container_width=True)

st.success(
    """
- **almost_churn**: 즉각적 개입 필요  
- **low_active**: 재활성화 유도 구간  
- **recoverable**: 구조 개선 시 정상 전환 가능
"""
)