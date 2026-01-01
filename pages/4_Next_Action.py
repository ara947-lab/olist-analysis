import streamlit as st


import streamlit as st

st.title("🤔 Next Action 제안")

# 핵심 결론은 '문장'이 아니라 '결정문'
st.success("결론: 이탈은 리뷰 문제가 아니라 **행동 감소(주문·활동)** 에서 시작된다.")

st.markdown("---")

st.subheader("📌 데이터 기반 판단")

st.markdown("""
- ❌ 리뷰 점수는 **이탈의 원인 아님**
- ⚠️ 주문 수·활동 일수 감소가 **가장 빠른 선행 신호**
- 📊 매출 감소는 **행동 감소 이후에 발생**
""")

st.markdown("---")

st.subheader("🚦 Risk Stage별 실행 전략")

with st.expander("🔴 almost_churn (주문 ≤ 1)"):
    st.markdown("""
    **상태**
    - 활동 거의 중단
    - 자연 회복 가능성 매우 낮음

    **즉시 액션**
    - 강한 인센티브 중심 개입 (쿠폰, 수수료 완화)
    - 단기 성과 없을 경우 관리 우선순위 하향
    """)

with st.expander("🟠 low_active (주문 2~3)"):
    st.markdown("""
    **상태**
    - 이탈 초기 단계
    - 개입 효과 가장 큼

    **추천 액션**
    - 개인화 알림 / 노출 강화
    - 활동 일수 기준 Early Warning Trigger
    """)

with st.expander("🟢 normal"):
    st.markdown("""
    **상태**
    - 안정적 활동 유지

    **운영 원칙**
    - 적극 개입 불필요
    - Risk Stage 하락 여부만 모니터링
    """)