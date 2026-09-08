import datetime
import pandas as pd
import plotly.express as px
import requests
import streamlit as st

# 1. 페이지 설정
st.set_page_config(
    page_title="박스오피스 조회", page_icon="🎬", layout="wide"
)

st.title("🎬 박스오피스 조회")

# 2. 날짜 선택 기능 (최대 선택 가능 날짜: 어제)
yesterday = datetime.date.today() - datetime.timedelta(days=1)
selected_date = st.date_input(
    "조회할 날짜를 선택하세요",
    value=yesterday,
    max_value=yesterday,
    help="오늘 날짜는 집계 전이므로 어제 날짜까지 선택할 수 있습니다.",
)

# KOBIS API 키 불러오기
KOBIS_API_KEY = st.secrets["KOBIS_KEY"]
formatted_date = selected_date.strftime("%Y%m%d")

# 3. KOBIS API 데이터 요청
url = f"http://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json?key={KOBIS_API_KEY}&targetDt={formatted_date}"

try:
  response = requests.get(url)
  data = response.json()
  daily_list = data.get("boxOfficeResult", {}).get("dailyBoxOfficeList", [])

  # 4. 영화 목록이 비어있는 경우 처리
  if not daily_list:
    st.warning("그날은 아직 집계 전입니다.")
  else:
    # --- [상단] 1위 영화 하이라이트 ---
    top_movie = daily_list[0]
    st.header(f"🥇 1위 — {top_movie.get('movieNm')}")

    col1, col2, col3 = st.columns(3)
    col1.metric("관객수", f"{int(top_movie.get('audiCnt', 0)):,}명")
    col2.metric("누적 관객수", f"{int(top_movie.get('audiAcc', 0)):,}명")
    col3.metric("스크린수", f"{int(top_movie.get('scrnCnt', 0)):,}개")

    st.markdown("---")

    # --- [중단] 전체 순위표 데이터 가공 ---
    table_data = []
    chart_data = []

    for item in daily_list:
      rank = item.get("rank")
      movie_nm = item.get("movieNm", "")
      open_dt = item.get("openDt", "")
      audi_cnt = int(item.get("audiCnt", 0))
      audi_acc = int(item.get("audiAcc", 0))
      scrn_cnt = int(item.get("scrnCnt", 0))
      rank_inten = int(item.get("rankInten", 0))

      # 조건 1: 누적관객 100만 명 이상일 때 영화명 옆에 트로피 이모지 붙이기
      display_name = (
          f"{movie_nm} 🏆" if audi_acc >= 1_000_000 else movie_nm
      )

      # 조건 2: 순위 증감에 따른 화살표 및 표시 설정
      if rank_inten > 0:
        inten_str = f"🔺 {rank_inten}"  # 순위 상승 (빨간 위 화살표)
      elif rank_inten < 0:
        inten_str = f"🔹 {abs(rank_inten)}"  # 순위 하락 (파란 아래 화살표)
      else:
        inten_str = "-"  # 변동 없음

      table_data.append({
          "순위": rank,
          "영화명": display_name,
          "개봉일": open_dt,
          "관객수": f"{audi_cnt:,}",
          "누적관객": f"{audi_acc:,}",
          "스크린수": f"{scrn_cnt:,}",
          "순위 변동": inten_str,
      })

      # 차트용 데이터 수집
      chart_data.append({"영화명": movie_nm, "관객수": audi_cnt})

    df = pd.DataFrame(table_data)

    st.subheader(
        f"📋 {selected_date.strftime('%Y-%m-%d')} 박스오피스 순위표"
    )
    st.dataframe(df, use_container_width=True, hide_index=True)

    # --- [하단] 관객수 상위 5편 바 차트 ---
    st.markdown("---")
    st.subheader("📊 관객수 상위 5편")

    df_chart = pd.DataFrame(chart_data[:5])
    fig = px.bar(
        df_chart,
        x="영화명",
        y="관객수",
        text_auto=",.0f",
        labels={"영화명": "영화명", "관객수": "당일 관객수"},
    )
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
  st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
