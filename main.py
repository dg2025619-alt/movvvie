import numpy as np
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
# 2. 장르 안에 영화가 들어 있는 트리맵 (칸 크기 = 총 관객수)
# ----------------------------------------------------------------------------
st.header("2️⃣ 장르 속 영화들 - 트리맵")

fig_treemap = px.treemap(
    df,
    path=[px.Constant("전체"), "genre", "movieNm"],
    values="total_audi",
    labels={"genre": "장르", "movieNm": "영화명", "total_audi": "총 관객수"},
    title="장르별 영화 트리맵 (칸 크기 = 총 관객수)",
)
fig_treemap.update_traces(
    hovertemplate="영화명: %{label}<br>총 관객수: %{value:,}명<extra></extra>"
)
st.plotly_chart(fig_treemap, use_container_width=True)
insight_box(
    "insight_treemap",
    "예: OOO 영화가 속한 칸이 가장 커서, 이 영화가 총 관객수 1위임을 알 수 있다.",
)

st.divider()

# ----------------------------------------------------------------------------
# 3. 총 관객수 분포 - 히스토그램 (자동 분석 문구 포함)
# ----------------------------------------------------------------------------
st.header("3️⃣ 총 관객수의 분포")

N_BINS = 30
fig_audi_hist = px.histogram(
    df,
    x="total_audi",
    nbins=N_BINS,
    labels={"total_audi": "총 관객수"},
    title="총 관객수 분포",
)
fig_audi_hist.update_traces(
    hovertemplate="관객수 구간: %{x}<br>영화 수: %{y}편<extra></extra>"
)
fig_audi_hist.update_layout(yaxis_title="영화 수(편)")
st.plotly_chart(fig_audi_hist, use_container_width=True)

# 가장 영화가 몰려 있는 구간과, 총 관객수가 가장 많은 영화를 자동으로 계산
audi_valid = df["total_audi"].dropna()
counts, bin_edges = np.histogram(audi_valid, bins=N_BINS)
max_bin_idx = counts.argmax()
bin_low, bin_high = bin_edges[max_bin_idx], bin_edges[max_bin_idx + 1]

top_movie_row = df.loc[df["total_audi"].idxmax()]
top_movie_name = top_movie_row["movieNm"]
top_movie_audi = top_movie_row["total_audi"]

st.info(
    f"📊 영화 {int(counts[max_bin_idx])}편이 총 관객수 **{bin_low:,.0f}명 ~ {bin_high:,.0f}명** "
    f"구간에 가장 많이 몰려 있어요.\n\n"
    f"🏆 총 관객수가 가장 많은 영화는 **'{top_movie_name}'**로, 약 **{top_movie_audi:,.0f}명**을 동원했어요."
)

insight_box(
    "insight_audi_hist",
    "예: 총 관객수가 아주 많은 소수의 영화와, 그렇지 않은 다수의 영화로 나뉜다.",
)

st.divider()

# ----------------------------------------------------------------------------
# 4. 개봉일 스크린수와 총 관객수의 관계 - 산점도 (장르별 색)
# ----------------------------------------------------------------------------
st.header("4️⃣ 개봉일 스크린수와 총 관객수의 관계")

fig_scatter1 = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    color="genre",
    hover_name="movieNm",
    labels={"first_scrn": "개봉일 스크린수", "total_audi": "총 관객수", "genre": "장르"},
    title="개봉일 스크린수 vs 총 관객수 (장르별 색)",
)
st.plotly_chart(fig_scatter1, use_container_width=True)
insight_box(
    "insight_scatter1",
    "예: 개봉일에 스크린을 많이 확보할수록 총 관객수도 대체로 많아지는 경향이 있다.",
)

st.divider()

# ----------------------------------------------------------------------------
# 5. 영화 10편 이상인 장르만 골라 - 장르별 총 관객수 박스플롯
# ----------------------------------------------------------------------------
st.header("5️⃣ 장르별 총 관객수 분포 (10편 이상인 장르만)")

genre_movie_counts = df["genre"].value_counts()
major_genres = genre_movie_counts[genre_movie_counts >= 10].index
df_major_genres = df[df["genre"].isin(major_genres)]

fig_box = px.box(
    df_major_genres,
    x="genre",
    y="total_audi",
    color="genre",
    hover_name="movieNm",
    points="outliers",
    labels={"genre": "장르", "total_audi": "총 관객수"},
    title="장르별 총 관객수 분포 (영화 10편 이상인 장르만)",
)
fig_box.update_layout(showlegend=False)
st.plotly_chart(fig_box, use_container_width=True)
st.caption(f"포함된 장르({len(major_genres)}개): " + ", ".join(major_genres))
insight_box(
    "insight_box",
    "예: 장르에 따라 총 관객수의 범위와 흩어진 정도가 다르고, 상자 밖으로 튀는 영화(이상치)도 있다.",
)

st.divider()

# ----------------------------------------------------------------------------
# 6. 개봉일 스크린수 · 총 관객수 · 첫 주 관객수 - 버블 그래프
# ----------------------------------------------------------------------------
st.header("6️⃣ 개봉일 스크린수와 총 관객수의 관계 - 버블 그래프")

fig_bubble = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    size="first_week_audi",
    color="genre",
    hover_name="movieNm",
    size_max=45,
    labels={
        "first_scrn": "개봉일 스크린수",
        "total_audi": "총 관객수",
        "first_week_audi": "첫 주 관객수",
        "genre": "장르",
    },
    title="개봉일 스크린수 vs 총 관객수 (원 크기 = 첫 주 관객수)",
)
st.plotly_chart(fig_bubble, use_container_width=True)
insight_box(
    "insight_bubble",
    "예: 원이 큰(첫 주 관객이 많은) 영화일수록 총 관객수도 많은 편이다.",
)

st.divider()

# ----------------------------------------------------------------------------
# 7. 제작 국가 -> 장르 - 선버스트 그래프 (칸 크기 = 영화 편수)
# ----------------------------------------------------------------------------
st.header("7️⃣ 제작 국가와 장르의 관계 - 선버스트")

nation_genre_counts = (
    df.groupby(["nation", "genre"]).size().reset_index(name="편수")
)

fig_sunburst = px.sunburst(
    nation_genre_counts,
    path=["nation", "genre"],
    values="편수",
    labels={"nation": "제작 국가", "genre": "장르", "편수": "영화 편수"},
    title="제작 국가 -> 장르 선버스트 (칸 크기 = 영화 편수)",
)
fig_sunburst.update_traces(
    hovertemplate="%{label}<br>영화 편수: %{value}편<extra></extra>"
)
st.plotly_chart(fig_sunburst, use_container_width=True)
insight_box(
    "insight_sunburst",
    "예: 특정 국가는 특정 장르에 치우쳐 있고, 다른 국가는 장르가 고르게 퍼져 있다.",
)

st.divider()

# ----------------------------------------------------------------------------
# 9. 개봉월 -> 장르 - 트리맵 (칸 크기 = 총 관객수 합)
# ----------------------------------------------------------------------------
st.header("9️⃣ 개봉월별 장르 흥행 - 트리맵")

df_month = df.dropna(subset=["openDt"]).copy()
df_month["openMonth"] = df_month["openDt"].dt.strftime("%m월")

month_genre_sum = (
    df_month.groupby(["openMonth", "genre"])["total_audi"].sum().reset_index()
)

fig_treemap2 = px.treemap(
    month_genre_sum,
    path=[px.Constant("전체"), "openMonth", "genre"],
    values="total_audi",
    labels={"openMonth": "개봉월", "genre": "장르", "total_audi": "총 관객수 합"},
    title="개봉월별 장르 흥행 트리맵 (칸 크기 = 총 관객수 합)",
)
fig_treemap2.update_traces(
    hovertemplate="%{label}<br>총 관객수 합: %{value:,}명<extra></extra>"
)
st.plotly_chart(fig_treemap2, use_container_width=True)
insight_box(
    "insight_treemap2",
    "예: OO월에는 OO 장르가 유독 큰 칸을 차지해서, 그 달에 그 장르 영화가 흥행을 주도했음을 알 수 있다.",
)

st.divider()

st.caption("데이터 출처: KOBIS(영화관입장권통합전산망) 박스오피스 10위권 영화 요약표(greatsong/modudata)")
