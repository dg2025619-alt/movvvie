import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ----------------------------------------------------------------------------
# 기본 설정
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide",
)

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_URL)

    # 장르가 '세로막대(|) 기호'로 여러 개 적혀 있으면 첫 번째 장르만 사용
    df["genre"] = df["genre"].astype(str).str.split("|").str[0].str.strip()

    # 개봉일(여덟 자리 숫자, 예: 20230115)을 날짜형으로 변환
    df["openDt"] = pd.to_datetime(df["openDt"], format="%Y%m%d", errors="coerce")

    # 숫자 열 형 변환(문자열로 섞여 들어오는 경우 대비)
    numeric_cols = [
        "first_scrn",
        "first_show",
        "first_week_audi",
        "total_audi",
        "days_in_top10",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def insight_box(key: str, placeholder: str) -> None:
    """그래프 아래에 '이 그래프로 알 수 있는 것'을 적는 칸을 만든다."""
    st.text_area(
        "💡 이 그래프로 알 수 있는 것",
        placeholder=placeholder,
        key=key,
        height=80,
    )


# ----------------------------------------------------------------------------
# 데이터 불러오기
# ----------------------------------------------------------------------------
st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.markdown(
    """
1년간 박스오피스 10위권에 들었던 영화 216편의 자료를 가지고,
**흩어진 정도(분포)** 와 **두 항목 사이의 관계**를 여러 그래프로 살펴보는 페이지예요.
그래프를 살펴본 뒤, 아래 칸에 스스로 알아낸 점을 한 문장씩 적어 보세요.
"""
)

try:
    df = load_data()
except Exception as e:
    st.error(f"데이터를 불러오는 중 문제가 생겼어요: {e}")
    st.stop()

with st.expander("📄 원본 데이터 미리 보기"):
    st.dataframe(df, use_container_width=True)

st.divider()

# ----------------------------------------------------------------------------
# 1. 장르별 영화 편수 - 도넛 그래프
# ----------------------------------------------------------------------------
st.header("1️⃣ 장르별 영화 편수")

genre_counts = (
    df["genre"].value_counts().reset_index().rename(columns={"count": "편수", "genre": "장르"})
)
if "index" in genre_counts.columns:  # pandas 버전에 따라 열 이름이 다를 수 있음
    genre_counts = genre_counts.rename(columns={"index": "장르"})

fig_donut = go.Figure(
    data=[
        go.Pie(
            labels=genre_counts["장르"],
            values=genre_counts["편수"],
            hole=0.5,
            hovertemplate="장르: %{label}<br>편수: %{value}편<br>비율: %{percent}<extra></extra>",
            textinfo="label+percent",
        )
    ]
)
fig_donut.update_layout(
    title="장르별 영화 편수 비율",
    legend_title="장르",
)
st.plotly_chart(fig_donut, use_container_width=True)
insight_box(
    "insight_genre_donut",
    "예: 액션 장르가 전체의 O%를 차지해서 가장 많이 만들어졌다.",
)

st.divider()

# ----------------------------------------------------------------------------
# 2. 개봉일 스크린 수 분포 - 히스토그램
# ----------------------------------------------------------------------------
st.header("2️⃣ 개봉일 스크린 수의 분포")

fig_scrn_hist = px.histogram(
    df,
    x="first_scrn",
    nbins=30,
    labels={"first_scrn": "개봉일 스크린수"},
    title="개봉일 스크린 수 분포",
)
fig_scrn_hist.update_traces(
    hovertemplate="스크린수 구간: %{x}<br>영화 수: %{y}편<extra></extra>"
)
fig_scrn_hist.update_layout(yaxis_title="영화 수(편)")
st.plotly_chart(fig_scrn_hist, use_container_width=True)
insight_box(
    "insight_scrn_hist",
    "예: 대부분의 영화는 개봉일 스크린수가 O~O개 사이에 몰려 있다.",
)

st.divider()

# ----------------------------------------------------------------------------
# 3. 총 관객수 분포 - 히스토그램
# ----------------------------------------------------------------------------
st.header("3️⃣ 총 관객수의 분포")

fig_audi_hist = px.histogram(
    df,
    x="total_audi",
    nbins=30,
    labels={"total_audi": "총 관객수"},
    title="총 관객수 분포",
)
fig_audi_hist.update_traces(
    hovertemplate="관객수 구간: %{x}<br>영화 수: %{y}편<extra></extra>"
)
fig_audi_hist.update_layout(yaxis_title="영화 수(편)")
st.plotly_chart(fig_audi_hist, use_container_width=True)
insight_box(
    "insight_audi_hist",
    "예: 총 관객수가 아주 많은 소수의 영화와, 그렇지 않은 다수의 영화로 나뉜다.",
)

st.divider()

# ----------------------------------------------------------------------------
# 4. 10위권 유지 일수 분포 - 히스토그램
# ----------------------------------------------------------------------------
st.header("4️⃣ 박스오피스 10위권 유지 일수의 분포")

fig_days_hist = px.histogram(
    df,
    x="days_in_top10",
    nbins=20,
    labels={"days_in_top10": "10위권 유지 일수"},
    title="10위권 유지 일수 분포",
)
fig_days_hist.update_traces(
    hovertemplate="유지 일수 구간: %{x}<br>영화 수: %{y}편<extra></extra>"
)
fig_days_hist.update_layout(yaxis_title="영화 수(편)")
st.plotly_chart(fig_days_hist, use_container_width=True)
insight_box(
    "insight_days_hist",
    "예: 대부분의 영화는 10위권에 O일 이내로 머무른다.",
)

st.divider()

# ----------------------------------------------------------------------------
# 5. 제작 국가별 영화 편수 - 막대 그래프
# ----------------------------------------------------------------------------
st.header("5️⃣ 제작 국가별 영화 편수")

nation_counts = df["nation"].value_counts().reset_index()
nation_counts.columns = ["국가", "편수"]

fig_nation_bar = px.bar(
    nation_counts,
    x="국가",
    y="편수",
    title="제작 국가별 영화 편수",
    labels={"국가": "제작 국가", "편수": "영화 수(편)"},
)
fig_nation_bar.update_traces(
    hovertemplate="국가: %{x}<br>영화 수: %{y}편<extra></extra>"
)
st.plotly_chart(fig_nation_bar, use_container_width=True)
insight_box(
    "insight_nation_bar",
    "예: 국내(한국) 영화와 외국 영화 중 어느 쪽이 더 많이 10위권에 들었는지 알 수 있다.",
)

st.divider()

# ----------------------------------------------------------------------------
# 6. 개봉일 스크린수와 총 관객수의 관계 - 산점도
# ----------------------------------------------------------------------------
st.header("6️⃣ 개봉일 스크린수와 총 관객수의 관계")

fig_scatter1 = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    color="genre",
    hover_name="movieNm",
    labels={"first_scrn": "개봉일 스크린수", "total_audi": "총 관객수", "genre": "장르"},
    title="개봉일 스크린수 vs 총 관객수",
)
st.plotly_chart(fig_scatter1, use_container_width=True)
insight_box(
    "insight_scatter1",
    "예: 개봉일에 스크린을 많이 확보할수록 총 관객수도 대체로 많아지는 경향이 있다.",
)

st.divider()

# ----------------------------------------------------------------------------
# 7. 개봉 첫 주 관객수와 총 관객수의 관계 - 산점도
# ----------------------------------------------------------------------------
st.header("7️⃣ 개봉 첫 주 관객수와 총 관객수의 관계")

fig_scatter2 = px.scatter(
    df,
    x="first_week_audi",
    y="total_audi",
    color="genre",
    hover_name="movieNm",
    labels={
        "first_week_audi": "개봉 첫 주 관객수",
        "total_audi": "총 관객수",
        "genre": "장르",
    },
    title="개봉 첫 주 관객수 vs 총 관객수",
)
st.plotly_chart(fig_scatter2, use_container_width=True)
insight_box(
    "insight_scatter2",
    "예: 개봉 첫 주 관객수만 봐도 이 영화의 총 관객수를 어느 정도 예상할 수 있다.",
)

st.divider()

# ----------------------------------------------------------------------------
# 8. 장르별 총 관객수 분포 - 박스플롯
# ----------------------------------------------------------------------------
st.header("8️⃣ 장르별 총 관객수 분포")

fig_box = px.box(
    df,
    x="genre",
    y="total_audi",
    color="genre",
    hover_name="movieNm",
    labels={"genre": "장르", "total_audi": "총 관객수"},
    title="장르별 총 관객수 분포",
)
fig_box.update_layout(showlegend=False)
st.plotly_chart(fig_box, use_container_width=True)
insight_box(
    "insight_box",
    "예: 장르에 따라 총 관객수의 범위와 흩어진 정도가 다르게 나타난다.",
)

st.divider()

st.caption("데이터 출처: KOBIS(영화관입장권통합전산망) 박스오피스 10위권 영화 요약표(greatsong/modudata)")
