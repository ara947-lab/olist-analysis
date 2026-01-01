import os
import pandas as pd
import streamlit as st
import folium
from folium.plugins import HeatMap, MarkerCluster
import streamlit.components.v1 as components

# =========================
# Cache Clear (단독 실행)
# =========================
st.cache_data.clear()

# =========================
# Page Config
# =========================
st.set_page_config(
    page_title="지리 분석",
    layout="wide"
)

# =========================
# Data Load
# =========================
@st.cache_data
def load_geo_data():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")

    geo = pd.read_csv(
        os.path.join(data_dir, "geo_preprocessed.csv"),
        encoding="latin-1",
        encoding_errors="replace"
    )

    sellers = pd.read_csv(
        os.path.join(data_dir, "olist_sellers_dataset.csv"),
        encoding="latin-1",
        encoding_errors="replace"
    )

    customers = pd.read_csv(
        os.path.join(data_dir, "olist_customers_dataset.csv"),
        encoding="latin-1",
        encoding_errors="replace"
    )

    sellers_geo = sellers.merge(
        geo,
        left_on="seller_zip_code_prefix",
        right_on="zip_code_prefix",
        how="left"
    )

    customers_geo = customers.merge(
        geo,
        left_on="customer_zip_code_prefix",
        right_on="zip_code_prefix",
        how="left"
    )

    return sellers_geo, customers_geo


sellers_geo, customers_geo = load_geo_data()

# =========================
# Title
# =========================
st.title("🗺️ 판매자 / 구매자 지리 분석")
st.caption("브라질 내 판매자와 구매자의 지역 분포 현황")

# =========================
# Sidebar
# =========================
st.sidebar.header("⚙️ 지리 분석 설정")

map_type = st.sidebar.radio(
    "지도 유형",
    ["판매자 히트맵", "구매자 히트맵", "통합 비교"]
)

sample_size = st.sidebar.slider(
    "샘플 크기",
    1000, 10000, 5000, 1000
)

# =========================
# KPI
# =========================
c1, c2, c3 = st.columns(3)

c1.metric("🏪 총 판매자", f"{len(sellers_geo):,}명")
c2.metric("👥 총 구매자", f"{len(customers_geo):,}명")
c3.metric(
    "📊 판매자 / 구매자 비율",
    f"{len(sellers_geo) / len(customers_geo) * 100:.2f}%"
)

st.divider()

# =========================
# Map Data
# =========================
brazil_center = [-14, -53.25]

seller_valid = sellers_geo.dropna(subset=["lat", "lng"])
customer_valid = customers_geo.dropna(subset=["lat", "lng"])

def safe_sample(df, n, random_state=42):
    if len(df) == 0:
        return df
    return df.sample(n=min(n, len(df)), random_state=random_state)

seller_sample = safe_sample(seller_valid, sample_size)
customer_sample = safe_sample(customer_valid, sample_size)

# =========================
# Map Render
# =========================
m = folium.Map(location=brazil_center, zoom_start=4, tiles="cartodbpositron")

if map_type == "판매자 히트맵" and len(seller_sample) > 0:
    HeatMap(seller_sample[["lat", "lng"]].values.tolist(), radius=10, blur=15).add_to(m)

elif map_type == "구매자 히트맵" and len(customer_sample) > 0:
    HeatMap(customer_sample[["lat", "lng"]].values.tolist(), radius=8, blur=12).add_to(m)

else:
    if len(seller_sample) > 0:
        HeatMap(
            seller_sample[["lat", "lng"]].values.tolist(),
            radius=10,
            blur=15,
            name="판매자"
        ).add_to(m)

    if len(customer_sample) > 0:
        cluster = MarkerCluster(name="구매자")
        for _, r in customer_sample.iterrows():
            folium.CircleMarker(
                location=[r["lat"], r["lng"]],
                radius=3,
                color="blue",
                fill=True,
                fill_opacity=0.6
            ).add_to(cluster)
        cluster.add_to(m)

    folium.LayerControl().add_to(m)

components.html(m._repr_html_(), height=600)

# =========================
# State Table
# =========================
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

st.dataframe(state_df.sort_values("구매자수", ascending=False).head(10), use_container_width=True)

# =========================
# Insight
# =========================
st.subheader("💡 핵심 인사이트")

top3_seller = sellers_geo["state"].value_counts().head(3)
top3_customer = customers_geo["state"].value_counts().head(3)

seller_conc = top3_seller.sum() / len(sellers_geo) * 100
customer_conc = top3_customer.sum() / len(customers_geo) * 100

st.write(f"""
- **판매자 집중도**: 상위 3개 주에 {seller_conc:.1f}%  
- **구매자 집중도**: 상위 3개 주에 {customer_conc:.1f}%  
- **차이**: 판매자가 {seller_conc - customer_conc:.1f}%p 더 집중
""")

if seller_conc > customer_conc + 10:
    st.warning("⚠️ 판매자 지역 집중 → 배송 지연 리스크 가능")
