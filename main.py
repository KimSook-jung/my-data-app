import datetime
import pandas as pd
import plotly.express as px
import requests
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="어제의 박스오피스",
    page_icon="🎬",
    layout="wide"
)

# KOBIS API URL
URL = "https://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"

# 비밀 금고(secrets)에서 KOBIS_KEY 불러오기
if "KOBIS_KEY" not in st.secrets:
    st.error("Secrets에 KOBIS_KEY가 설정되지 않았습니다. Manage app -> Settings -> Secrets에 KOBIS_KEY를 등록해 주세요.")
    st.stop()

API_KEY = st.secrets["KOBIS_KEY"]

# 한국 시간(KST) 기준으로 '어제' 날짜 계산 (배포 서버 시계 차이 대비)
KST = datetime.timezone(datetime.timedelta(hours=9))
yesterday = datetime.datetime.now(KST).date() - datetime.timedelta(days=1)
target_dt = yesterday.strftime("%Y%m%d")

# 캐싱 적용: 같은 날짜 데이터는 1시간(3600초) 동안 기억하여 API 중복 호출 방지
@st.cache_data(ttl=3600)
def fetch_boxoffice(date_str):
    """KOBIS API에서 해당 날짜의 일별 박스오피스를 받아오는 함수"""
    params = {
        "key": API_KEY,
        "targetDt": date_str
    }
    response = requests.get(URL, params=params, timeout=10)
    response.raise_for_status()
    return response.json()

# 화면 타이틀 및 안내
st.title("🎬 어제의 박스오피스")
st.caption(f"조회 날짜: {yesterday.strftime('%Y년 %m월 %d일')} (한국 시간 기준 어제)")

# API 데이터 불러오기 및 예외 처리
try:
    data = fetch_boxoffice(target_dt)
except requests.RequestException:
    st.error("KOBIS API 서버에 연결하지 못했습니다. 네트워크 상태나 요청 주소를 확인해 주세요.")
    st.stop()

# 인증키 오류 발생 시 faultInfo 처리 (KOBIS API는 키 오류 시에도 HTTP 200 반환)
if "faultInfo" in data:
    fault = data["faultInfo"]
    st.error(f"API 호출 오류가 발생했습니다: {fault.get('message', '알 수 없는 오류')}")
    st.info("비밀 금고(Secrets)에 등록된 KOBIS_KEY 값이 올바른지 확인해 주세요.")
    st.stop()

# 영화 목록 추출
movies = data.get("boxOfficeResult", {}).get("dailyBoxOfficeList", [])

# 영화 목록이 비어있는 경우 처리
if not movies:
    st.warning("박스오피스 데이터가 비어 있습니다. 해당 날짜의 집계가 완료되었는지 확인해 주세요.")
    st.stop()

# 데이터프레임 변환
df = pd.DataFrame(movies)

# 문자열로 들어오는 숫자 데이터를 정수형(int)으로 변환
numeric_cols = ["rank", "audiCnt", "audiAcc", "scrnCnt"]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col])

# 순위 기준으로 정렬
df = df.sort_values("rank")

# ---------------------------------------------------------
# 1. 1위 영화 지표 카드 표시
# ---------------------------------------------------------
top_movie = df.iloc[0]
st.subheader(f"🥇 1위 영화: {top_movie['movieNm']}")

col1, col2, col3 = st.columns(3)
col1.metric("어제 관객수", f"{top_movie['audiCnt']:,} 명")
col2.metric("누적 관객수", f"{top_movie['audiAcc']:,} 명")
col3.metric("스크린수", f"{top_movie['scrnCnt']:,} 개")

st.markdown("---")

# ---------------------------------------------------------
# 2. 순위표 표시
# ---------------------------------------------------------
st.subheader("📋 전체 박스오피스 순위표")

# 표시할 열 선택 및 이름 변경
table_df = df[["rank", "movieNm", "openDt", "audiCnt", "audiAcc", "scrnCnt"]].copy()
table_df.columns = ["순위", "영화명", "개봉일", "관객수", "누적관객", "스크린수"]

st.dataframe(
    table_df,
    use_container_width=True,
    hide_index=True
)

st.markdown("---")

# ---------------------------------------------------------
# 3. 관객수 상위 5편 막대그래프
# ---------------------------------------------------------
st.subheader("📊 관객수 상위 5편")

top5_df = df.nlargest(5, "audiCnt")

fig = px.bar(
    top5_df,
    x="movieNm",
    y="audiCnt",
    labels={"movieNm": "영화명", "audiCnt": "어제 관객수"},
    text_auto=",d",
    title="상위 5개 영화 관객수 비교"
)

fig.update_traces(textposition="outside")
fig.update_layout(xaxis_title="영화명", yaxis_title="관객수 (명)")

st.plotly_chart(fig, use_container_width=True)
