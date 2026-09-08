import datetime
import pandas as pd
import requests
import streamlit as st

# 1. 페이지 설정
st.set_page_config(page_title="박스오피스 조회", page_icon="🎬", layout="wide")

st.title("🎬 박스오피스 조회")

# 2. 날짜 선택 기능 (최대 선택 가능 날짜: 어제)
yesterday = datetime.date.today() - datetime.timedelta(days=1)
selected_date = st.date_input(
    "조회할 날짜를 선택하세요",
    value=yesterday,
    max_value=yesterday,
    help="오늘 날짜는 집계 전이므로 어제 날짜까지 선택할 수 있습니다.",
)

# KOBIS API 키 (Secrets 관리 권장)
# 기존 (오류 발생)
# KOBIS_API_KEY = st.secrets["495e52df5baa4f5a4aaa3473cc414e20"]

# 수정 (정상)
KOBIS_API_KEY = st.secrets["KOBIS_API_KEY"]

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
    table_data = []

    for item in daily_list:
      rank = item.get("rank")
      movie_nm = item.get("movieNm", "")
      audi_acc = int(item.get("audiAcc", 0))
      audi_cnt = int(item.get("audiCnt", 0))
      rank_inten = int(item.get("rankInten", 0))

      # 조건 1: 누적관객 100만 명 이상일 때 트로피 이모지 붙이기
      display_name = (
          f"🏆 {movie_nm}" if audi_acc >= 1_000_000 else movie_nm
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
          "당일 관객수": f"{audi_cnt:,} 명",
          "누적 관객수": f"{audi_acc:,} 명",
          "순위 변동": inten_str,
      })

    # DataFrame 생성 및 테이블 출력
    df = pd.DataFrame(table_data)

    st.subheader(f"📅 {selected_date.strftime('%Y년 %m월 %d일')} 순위표")
    st.dataframe(df, use_container_width=True, hide_index=True)

except Exception as e:
  st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
