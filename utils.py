import pandas as pd
import streamlit as st
import os

@st.cache_data
def load_data():
    # 현재 파일(utils.py)이 있는 위치를 기준으로 절대 경로를 계산합니다.
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(BASE_DIR, "data", "seller_6m.csv")

    # pandas를 이용해 seller_6m.csv 파일을 읽어옵니다.
    df = pd.read_csv(csv_path)
    return df