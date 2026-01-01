import os
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap, MarkerCluster

# -------------------------
# Page Config
# -------------------------
st.set_page_config(
    page_title="지리 분석",
    layout="wide"
)

# -------------------------
# Data Load
# -------------------------
@st.cache_data
def load_geo_data():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")

    # 1. 전처리된 가벼운 파일(1MB)을 불러옵니다. (에러 방지 옵션 추가)
    geo_avg = pd.read_csv(os.path.join(data_dir, "geo_preprocessed.csv"), encoding="cp1252", errors="replace")
    
    # 2. 판매자 및 구매자 데이터 로드
    df_sellers = pd.read_csv(os.path.join(data_dir, "olist_sellers_dataset.csv"), encoding="cp1252", errors="replace")
    df_customers = pd.read_csv(os.path.join(data_dir, "olist_customers_dataset.csv"), encoding="cp1252", errors="replace")

    # 3. 데이터 병합(merge)
    sellers_geo = df_sellers.merge(geo_avg, left_on="seller_zip_code_prefix", right_on="zip_code_prefix", how="left")
    customers_geo = df_customers.merge(geo_avg, left_on="customer_zip_code_prefix", right_on="zip_code_prefix", how="left")

    return sellers_geo, customers_geo

sellers_geo, customers_geo = load_geo_data()

# =========================================================================
# 페이지 콘텐츠
# =========================================================================
if sellers_geo is None or customers_geo is None:
    st.error("❌ 지리 분석 데이터를 로드할 수 없습니다.")
    st.stop()

st.title("🗺️ 판매자/구매자 지리 분석")
st.caption("브라질 내 판매자와 구매자의 지역 분포 현황")

# -------------------------
# Sidebar
# -------------------------
st.sidebar.header("⚙️ 지리 분석 설정")

map_type = st.sidebar.radio(
    "지도 유형",
    ["판매자 히트맵", "구매자 히트맵", "통합 비교"]
)

sample_size = st.sidebar.slider(
    "샘플 크기",
    min_value=1000,
    max_value=10000,
    value=5000,
    step=1000
)

# -------------------------
# KPI
# -------------------------
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("🏪 총 판매자", f"{len(sellers_geo):,}명")
with col2:
    st.metric("👥 총 구매자", f"{len(customers_geo):,}명")
with col3:
    ratio = len(sellers_geo) / len(customers_geo) * 100
    st.metric("📊 판매자/구매자 비율", f"{ratio:.2f}%")

st.divider()

# -------------------------
# Map Data & Render
# -------------------------
brazil_center = [-14, -53.25]
seller_valid = sellers_geo.dropna(subset=["lat", "lng"])
customer_valid = customers_geo.dropna(subset=["lat", "lng"])

seller_sample = seller_valid.sample(n=min(sample_size, len(seller_valid)), random_state=42)
customer_sample = customer_valid.sample(n=min(sample_size, len(customer_valid)), random_state=42)

import streamlit.components.v1 as components

m = folium.Map(location=brazil_center, zoom_start=4, tiles="cartodbpositron")

if map_type == "판매자 히트맵":
    HeatMap(seller_sample[["lat", "lng"]].values.tolist(), radius=10, blur=15).add_to(m)
elif map_type == "구매자 히트맵":
    HeatMap(customer_sample[["lat", "lng"]].values.tolist(), radius=8, blur=12).add_to(m)
else:
    HeatMap(seller_sample[["lat", "lng"]].values.tolist(), radius=10, blur=15, name="판매자").add_to(m)
    customer_cluster = MarkerCluster(name="구매자 위치")
    for _, row in customer_sample.iterrows():
        folium.CircleMarker(location=[row["lat"], row["lng"]], radius=3, color="blue", fill=True).add_to(customer_cluster)
    customer_cluster.add_to(m)

components.html(m._repr_html_(), height=600)

st.divider()
st.subheader("📊 주(State)별 분포")
# (이하 생략 - 이전 로직 동일)
