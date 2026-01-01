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
    page_title="ьзАыж?ы╢ДьДЭ",
    layout="wide"
)

# -------------------------
# Data Load
# -------------------------
@st.cache_data
def load_geo_data():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")

    # 1. ?Ры│╕(58MB) ?А???░ыжмъ░А ызМыУа ъ░Аы▓╝ьЪ┤ ?Дь▓Шыж??МьЭ╝(1MB)??ы╢ИыЯм?╡ыЛИ??
    geo_avg = pd.read_csv(os.path.join(data_dir, "geo_preprocessed.csv"), encoding=" cp1252\, encoding_errors=\replace\)
    
    # 2. ?Рызд??ы░?ъ╡мызд???░ьЭ┤??ыбЬыУЬ
    df_sellers = pd.read_csv(os.path.join(data_dir, "olist_sellers_dataset.csv"), encoding=" cp1252\, encoding_errors=\replace\)
    df_customers = pd.read_csv(os.path.join(data_dir, "olist_customers_dataset.csv"), encoding=" cp1252\, encoding_errors=\replace\)

    # 3. ?┤ы? ?Дь▓Шыжмъ? ?ШьЦ┤ ?ИьЬ╝ыпАыб?groupby ъ│╝ьаХ ?ЖьЭ┤ ы░ФыбЬ ы│СэХй(merge)?йыЛИ??
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
# ?ШьЭ┤ьзА ь╜ШэЕРь╕?
# =========================================================================
if sellers_geo is None or customers_geo is None:
    st.error("??ьзАыж?ы╢ДьДЭ ?░ьЭ┤?░ы? ыбЬыУЬ?????ЖьК╡?ИыЛд.")
    st.stop()

st.title("?Ч║я╕??Рызд??ъ╡мызд??ьзАыж?ы╢ДьДЭ")
st.caption("ы╕МыЭ╝ьз????Рызд?Рь? ъ╡мызд?РьЭШ ьзА??ы╢ДэПм ?ДэЩй")

# -------------------------
# Sidebar
# -------------------------
st.sidebar.header("?Щя╕П ьзАыж?ы╢ДьДЭ ?дьаХ")

map_type = st.sidebar.radio(
    "ьзА???аэШХ",
    ["?Рызд???ИэК╕ыз?, "ъ╡мызд???ИэК╕ыз?, "?╡эХй ы╣Дъ╡Р"]
)

sample_size = st.sidebar.slider(
    "?ШэФМ ?мъ╕░",
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
    st.metric("?Пк ь┤??Рызд??, f"{len(sellers_geo):,}ык?)
with col2:
    st.metric("?Се ь┤?ъ╡мызд??, f"{len(customers_geo):,}ык?)
with col3:
    ratio = len(sellers_geo) / len(customers_geo) * 100
    st.metric("?УК ?Рызд??ъ╡мызд??ы╣ДьЬи", f"{ratio:.2f}%")

st.divider()

# -------------------------
# Map Data
# -------------------------
brazil_center = [-14, -53.25]

seller_valid = sellers_geo.dropna(subset=["lat", "lng"])

seller_sample = seller_valid.sample(
    n=min(sample_size, len(seller_valid)),
    random_state=42
)

customer_valid = customers_geo.dropna(subset=["lat", "lng"])

customer_sample = customer_valid.sample(
    n=min(sample_size, len(customer_valid)),
    random_state=42
)

# -------------------------
# Map Render
# -------------------------
import streamlit.components.v1 as components

if map_type == "?Рызд???ИэК╕ыз?:
    st.subheader("?Рызд??ы╢ДэПм ?ИэК╕ыз?)

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

elif map_type == "ъ╡мызд???ИэК╕ыз?:
    st.subheader("ъ╡мызд??ы╢ДэПм ?ИэК╕ыз?)

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
    st.subheader("?Рызд??vs ъ╡мызд??ы╢ДэПм ы╣Дъ╡Р")

    m = folium.Map(
        location=brazil_center,
        zoom_start=4,
        tiles="cartodbpositron"
    )

    # ???Рызд?? ?ИэК╕ыз?
    HeatMap(
        seller_sample[["lat", "lng"]].values.tolist(),
        radius=10,
        blur=15,
        name="?Рызд???ИэК╕ыз?
    ).add_to(m)

    # ??ъ╡мызд?? ызИь╗д ?┤ыЯм?дэД░
    customer_cluster = MarkerCluster(name="ъ╡мызд???Дь╣Ш")

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
st.subheader("?УК ьг?State)ы│?ы╢ДэПм")

seller_by_state = sellers_geo.groupby("state").size().reset_index(name="?Рызд?РьИШ")
customer_by_state = customers_geo.groupby("state").size().reset_index(name="ъ╡мызд?РьИШ")

state_df = (
    seller_by_state
    .merge(customer_by_state, on="state", how="outer")
    .fillna(0)
)

state_df["ы╣ДьЬи(%)"] = (state_df["?Рызд?РьИШ"] / state_df["ъ╡мызд?РьИШ"] * 100).round(2)
state_df = state_df.sort_values("ъ╡мызд?РьИШ", ascending=False).head(10)

st.dataframe(state_df, use_container_width=True)

# -------------------------
# Insight
# -------------------------
st.subheader("?Тб ?╡ьЛм ?╕ьВм?┤эК╕")

top3_seller = sellers_geo["state"].value_counts().head(3)
top3_customer = customers_geo["state"].value_counts().head(3)

seller_concentration = top3_seller.sum() / len(sellers_geo) * 100
customer_concentration = top3_customer.sum() / len(customers_geo) * 100

st.write(f"""
- **?Рызд??ьзСьдС??*: ?БьЬД 3ъ░?ьг╝ьЧР {seller_concentration:.1f}% ьзСьдС  
- **ъ╡мызд??ьзСьдС??*: ?БьЬД 3ъ░?ьг╝ьЧР {customer_concentration:.1f}% ьзСьдС  
- **ь░иьЭ┤**: ?Рызд?Ръ? ъ╡мызд?Ры│┤??{seller_concentration - customer_concentration:.1f}%p ??ьзСьдС??
""")

if seller_concentration > customer_concentration + 10:
    st.warning("?ая╕П ?Рызд?Ръ? ?╣ьаХ ьзА??ЧР ъ│╝ыПД?Шъ▓М ьзСьдС ??ы░░ьЖб ьзА??ыжмьКд??ъ░А??)
