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

    # ✅ 이미 전처리된 지오 데이터 (groupby 필요 없음)
    geo_avg = pd.read_csv(
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
# Page Content
# =========================================================================
st.title("🗺️ 판매자 / 구매자 지리 분석")
st.caption("브라질 내 판매자와 구매자의 지역 분포")

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
    1000, 10000, 5000, 1000
)

# -------------------------
# KPI
# -------------------------
c1, c2, c3 = st.columns(3)

c1.metric("🏪 총 판매자", f"{len(sellers_geo):,}")
c2.metric("👥 총 구매자", f"{len(customers_geo):,}")
c3.metric(
    "📊 판매자/구매자 비율",
    f"{len(sellers_geo) / len(customers_geo) * 100:.2f}%"
)

st.divider()

# -------------------------
# Map Data
# -------------------------
brazil_center = [-14, -53.25]

seller_sample = sellers_geo.dropna(subset=["lat", "lng"]) \
    .sample(n=min(sample_size, len(sellers_geo)), random_state=42)

customer_sample = customers_geo.dropna(subset=["lat", "lng"]) \
    .sample(n=min(sample_size, len(customers_geo)), random_state=42)

# -------------------------
# Map Render
# -------------------------
m = folium.Map(location=brazil_center, zoom_start=4, tiles="cartodbpositron")

if map_type in ["판매자 히트맵", "통합 비교"]:
    HeatMap(
        seller_sample[["lat", "lng"]].values.tolist(),
        radius=10,
        blur=15,
        name="판매자"
    ).add_to(m)

if map_type in ["구매자 히트맵", "통합 비교"]:
    HeatMap(
        customer_sample[["lat", "lng"]].values.tolist(),
        radius=8,
        blur=12,
        name="구매자"
    ).add_to(m)

folium.LayerControl().add_to(m)
components.html(m._repr_html_(), height=600)

st.divider()

# -------------------------
# State Table
# -------------------------
st.subheader("📊 주(State)별 분포")

state_df = (
    sellers_geo.groupby("state").size().rename("판매자수")
    .to_frame()
    .merge(
        customers_geo.groupby("state").size().rename("구매자수"),
        on="state",
        how="outer"
    )
    .fillna(0)
)

state_df["비율(%)"] = (state_df["판매자수"] / state_df["구매자수"] * 100).round(2)

st.dataframe(
    state_df.sort_values("구매자수", ascending=False).head(10),
    use_container_width=True
)
