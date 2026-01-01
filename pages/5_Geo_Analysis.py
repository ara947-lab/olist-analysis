import os
import pandas as pd
import streamlit as st
import folium
from folium.plugins import HeatMap, MarkerCluster
import streamlit.components.v1 as components


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

    # 🔑 핵심 수정: encoding + encoding_errors
    df_geo = pd.read_csv(
        os.path.join(data_dir, "geo_preprocessed.csv"),
        encoding="latin-1",
        encoding_errors="replace"
    )
    df_sellers = pd.read_csv(
        os.path.join(data_dir, "olist_sellers_dataset.csv"),
        encoding="latin-1",
        encoding_errors="replace"
    )
    df_customers = pd.read_csv(
        os.path.join(data_dir, "olist_customers_dataset.csv"),
        encoding="latin-1",
        encoding_errors="replace"
    )

    geo_avg = (
        df_geo
        .groupby("geolocation_zip_code_prefix")
        .agg(
            lat=("geolocation_lat", "mean"),
            lng=("geolocation_lng", "mean"),
            state=("geolocation_state", "first")
        )
        .reset_index()
        .rename(columns={"geolocation_zip_code_prefix": "zip_code_prefix"})
    )

    sellers_geo = df_sellers.merge(
        geo_avg,
        left_on="seller_zip_code_prefix",
        right_on="zip_code_prefix",
        how="left"
    )

    customers_geo = df_customers.merge(
        geo_avg,
        left_on="customer_zip_code_prefix",
        right_on="zip_code_prefix",
        how="left"
    )

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
# Map Data
# -------------------------
brazil_center = [-14, -53.25]

seller_valid = sellers_geo.dropna(subset=["lat", "lng"])
customer_valid = customers_geo.dropna(subset=["lat", "lng"])

seller_sample = seller_valid.sample(
    n=min(sample_size, len(seller_valid)),
    random_state=42
)

customer_sample = customer_valid.sample(
    n=min(sample_size, len(customer_valid)),
    random_state=42
)

# -------------------------
# Map Render
# -------------------------
if map_type == "판매자 히트맵":
    st.subheader("판매자 분포 히트맵")

    m = folium.Map(
        location=brazil_center,
        zoom_start=4,
        tiles="cartodbpositron"
    )

    HeatMap(
        seller_sample[["lat", "lng"]].values.tolist(),
        radius=10,
        blur=15
    ).add_to(m)

    components.html(m._repr_html_(), height=600)

elif map_type == "구매자 히트맵":
    st.subheader("구매자 분포 히트맵")

    m = folium.Map(
        location=brazil_center,
        zoom_start=4,
        tiles="cartodbpositron"
    )

    HeatMap(
        customer_sample[["lat", "lng"]].values.tolist(),
        radius=8,
        blur=12
    ).add_to(m)

    components.html(m._repr_html_(), height=600)

else:
    st.subheader("판매자 vs 구매자 분포 비교")

    m = folium.Map(
        location=brazil_center,
        zoom_start=4,
        tiles="cartodbpositron"
    )

    HeatMap(
        seller_sample[["lat", "lng"]].values.tolist(),
        radius=10,
        blur=15,
        name="판매자 히트맵"
    ).add_to(m)

    customer_cluster = MarkerCluster(name="구매자 위치")

    for _, row in customer_sample.iterrows():
        folium.CircleMarker(
            location=[row["lat"], row["lng"]],
            radius=3,
            color="blue",
            fill=True,
            fill_opacity=0.6
        ).add_to(customer_cluster)

    customer_cluster.add_to(m)

    components.html(m._repr_html_(), height=600)

st.divider()

# -------------------------
# State Table
# -------------------------
st.subheader("📊 주(State)별 분포")

seller_by_state = sellers_geo.groupby("state").size().reset_index(name="판매자수")
customer_by_state = customers_geo.groupby("state").size().reset_index(name="구매자수")

state_df = (
    seller_by_state
    .merge(customer_by_state, on="state", how="outer")
    .fillna(0)
)

state_df["비율(%)"] = (state_df["판매자수"] / state_df["구매자수"] * 100).round(2)
state_df = state_df.sort_values("구매자수", ascending=False).head(10)

st.dataframe(state_df, use_container_width=True)

# -------------------------
# Insight
# -------------------------
st.subheader("💡 핵심 인사이트")

top3_seller = sellers_geo["state"].value_counts().head(3)
top3_customer = customers_geo["state"].value_counts().head(3)

seller_concentration = top3_seller.sum() / len(sellers_geo) * 100
customer_concentration = top3_customer.sum() / len(customers_geo) * 100

st.write(f"""
- **판매자 집중도**: 상위 3개 주에 {seller_concentration:.1f}% 집중  
- **구매자 집중도**: 상위 3개 주에 {customer_concentration:.1f}% 집중  
- **차이**: 판매자가 구매자보다 {seller_concentration - customer_concentration:.1f}%p 더 집중됨
""")

if seller_concentration > customer_concentration + 10:
    st.warning("⚠️ 판매자가 특정 지역에 과도하게 집중 → 배송 지연 리스크 가능")
