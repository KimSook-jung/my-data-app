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

# 1. 연도별 평균 기온 계산 및 선 그래프
yearly_avg = (
    df.groupby("연도", as_index=False)["평균기온"]
    .mean()
    .round(1)
)

st.header("연평균 기온 추이")

fig1 = px.line(
    yearly_avg,
    x="연도",
    y="평균기온",
    labels={"연도": "연도", "평균기온": "연평균 기온 (℃)"},
    markers=True,
    title="서울의 연도별 평균 기온 변화",
)
fig1.update_traces(hovertemplate="%{x}년: %{y}℃")
st.plotly_chart(fig1, use_container_width=True)

# 2. 일별 평균기온 분포 히스토그램
st.header("일별 평균기온은 어느 구간에 몰려 있나")

fig2 = px.histogram(
    df,
    x="평균기온",
    nbins=50,
    labels={"평균기온": "일별 평균기온 (℃)"},
    title="일별 평균기온 분포 (히스토그램)",
)
st.plotly_chart(fig2, use_container_width=True)

# 3. 최저기온과 최고기온의 관계 산점도 추가
st.header("최저기온과 최고기온의 관계")

fig3 = px.scatter(
    df,
    x="최저기온",
    y="최고기온",
    opacity=0.2,
    labels={"최저기온": "최저기온 (℃)", "최고기온": "최고기온 (℃)"},
    title="일별 최저기온 vs 최고기온 (산점도)",
)
st.plotly_chart(fig3, use_container_width=True)
