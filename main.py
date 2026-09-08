import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="서울의 100년 기온 변화", layout="wide")
st.title("서울의 100년 연평균 기온 변화")

DATA_URL = (
    "https://raw.githubusercontent.com/greatsong/modudata/main/data/seoul.csv"
)


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)
    df["날짜"] = pd.to_datetime(df["날짜"])
    df["연도"] = df["날짜"].dt.year
    return df


df = load_data()

# 연도별 평균 기온 계산
yearly_avg = (
    df.groupby("연도", as_index=False)["평균기온"]
    .mean()
    .round(1)
)

st.header("연평균 기온 추이")

# Plotly 라인 차트 생성
fig = px.line(
    yearly_avg,
    x="연도",
    y="평균기온",
    labels={"연도": "연도", "평균기온": "연평균 기온 (℃)"},
    markers=True,
    title="서울의 연도별 평균 기온 변화",
)

fig.update_traces(hovertemplate="%{x}년: %{y}℃")
st.plotly_chart(fig, use_container_width=True)
