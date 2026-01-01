import streamlit as st
import pandas as pd
import plotly.express as px

st.title("🚦 Risk Stage 분석")

seller_6m = pd.read_csv("data/seller_6m.csv")

# ------------------
# 설명 블록 (시계열 강조)
# ------------------
st.info(
"""
Risk Stage는 가입 후 **초기 6개월 동안의 매출·주문·활동 흐름을 시계열로 요약**한 결과입니다.  
이 단계는 단순 분류가 아니라 **이탈 위험을 조기에 포착하기 위한 경고 신호**로 사용됩니다.
"""
)

# ------------------
# KPI: 관리 대상 수
# ------------------
risk_cnt = seller_6m[seller_6m["risk_stage"] != "normal"]["seller_id"].nunique()
total_cnt = seller_6m["seller_id"].nunique()

st.metric(
    "즉시 관리 대상 판매자 수",
    f"{risk_cnt:,}명",
    delta=f"{risk_cnt / total_cnt * 100:.1f}%"
)

# ------------------
# 그래프 1: 매출 분포
# ------------------
q25 = seller_6m["revenue_6m"].quantile(0.25)

fig1 = px.histogram(
    seller_6m,
    x="revenue_6m",
    nbins=50,
    title="6개월 매출 분포 및 하위 25% 기준선"
)
fig1.add_vline(x=q25, line_dash="dash", annotation_text="하위 25% 기준")

st.plotly_chart(fig1, use_container_width=True)
st.caption("→ Risk Stage 기준은 매출 하위 25%를 포함한 행동 지표 조합")

# ------------------
# 그래프 2: Risk Stage 분포
# ------------------
stage_cnt = (
    seller_6m
    .groupby("risk_stage")["seller_id"]
    .nunique()
    .reset_index(name="seller_count")
)

fig2 = px.bar(
    stage_cnt,
    x="risk_stage",
    y="seller_count",
    text="seller_count",
    title="Risk Stage별 판매자 분포"
)

st.plotly_chart(fig2, use_container_width=True)

# ------------------
# 그래프 3: 리뷰 점수
# ------------------
review_mean = (
    seller_6m
    .groupby("risk_stage")["avg_review_6m"]
    .mean()
    .reset_index()
)

fig3 = px.scatter(
    review_mean,
    x="risk_stage",
    y="avg_review_6m",
    title="Risk Stage별 평균 리뷰 점수 (차이 미미)"
)

fig3.update_layout(yaxis=dict(range=[3.5, 4.5]))
st.plotly_chart(fig3, use_container_width=True)
st.caption("→ 리뷰 점수는 이탈의 선행 지표가 아님")

# ------------------
# 실무 연결: 대상 ID 예시
# ------------------
st.markdown("---")
st.subheader("🧾 Risk Stage별 판매자 ID 목록")

tabs = st.tabs(
    ["🔴 almost_churn", "🟠 low_active", "🟡 recoverable", "🟢 normal"]
)

stage_map = {
    "🔴 almost_churn": "almost_churn",
    "🟠 low_active": "low_active",
    "🟡 recoverable": "recoverable",
    "🟢 normal": "normal"
}

for tab, stage_key in zip(tabs, stage_map.values()):
    with tab:
        stage_df = seller_6m[seller_6m["risk_stage"] == stage_key]

        st.caption(f"총 {stage_df['seller_id'].nunique():,}명")

        st.dataframe(
            stage_df[
                [
                    "seller_id",
                    "revenue_6m",
                    "orders_6m",
                    "active_days_6m",
                ]
            ]
            .sort_values("revenue_6m"),
            use_container_width=True
        )

