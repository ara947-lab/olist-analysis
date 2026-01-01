import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정 (이거 꼭!)
st.set_page_config(
    page_title="판매자 이탈 Risk 분석",
    layout="wide"
)

# 데이터 로드
@st.cache_data
def load_data():
    return pd.read_csv("data/seller_6m.csv")

seller_6m = load_data()