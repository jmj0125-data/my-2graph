import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide"
)

st.title("영화 데이터 그래프 도감 2 - 분포와 관계")

# 데이터 주소
DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"


# 데이터 불러오기
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 개봉일: 여덟 자리 숫자를 날짜로 변환
    df["openDt"] = pd.to_datetime(
        df["openDt"].astype(str),
        format="%Y%m%d",
        errors="coerce"
    )

    # 장르: 여러 장르가 있으면 첫 번째 장르만 사용
    df["genre"] = (
        df["genre"]
        .fillna("미상")
        .astype(str)
        .str.split("|")
        .str[0]
        .str.strip()
    )

    # 빈 장르는 미상으로 처리
    df.loc[df["genre"] == "", "genre"] = "미상"

    # 관객 수를 숫자로 변환
    df["first_scrn"] = pd.to_numeric(df["first_scrn"], errors="coerce")
    df["first_show"] = pd.to_numeric(df["first_show"], errors="coerce")
    df["first_week_audi"] = pd.to_numeric(
        df["first_week_audi"], errors="coerce"
    )
    df["total_audi"] = pd.to_numeric(
        df["total_audi"], errors="coerce"
    )
    df["days_in_top10"] = pd.to_numeric(
        df["days_in_top10"], errors="coerce"
    )

    return df


df = load_data()


# ============================================================
# 1. 장르별 영화 편수
# ============================================================

st.header("1. 장르별 영화 편수")

genre_count = (
    df["genre"]
    .value_counts()
    .reset_index()
)

genre_count.columns = ["장르", "영화편수"]

fig1 = px.pie(
    genre_count,
    names="장르",
    values="영화편수",
    hole=0.55,
    title="장르별 영화 편수"
)

fig1.update_traces(
    textinfo="label+percent",
    hovertemplate=(
        "<b>%{label}</b><br>"
        "영화 편수: %{value}편<br>"
        "비율: %{percent}<extra></extra>"
    )
)

fig1.update_layout(
    height=550,
    legend_title="장르"
)

st.plotly_chart(fig1, width="stretch")

# 설명 영역
st.markdown("---")
st.subheader("💡 이 그래프로 알 수 있는 것")
st.text_area(
    "설명 문장을 직접 작성해 보세요.",
    placeholder="예: 어떤 장르의 영화가 가장 많이 포함되어 있는지 알 수 있다.",
    key="graph1_description",
    height=80
)


# ============================================================
# 2. 장르별 영화 트리맵
# ============================================================

st.markdown("---")
st.header("2. 장르 안에 들어 있는 영화")

# 영화별 총 관객을 기준으로 트리맵 구성
treemap_data = df[
    ["genre", "movieNm", "total_audi"]
].copy()

# 영화명이 비어 있는 경우 제외
treemap_data = treemap_data[
    treemap_data["movieNm"].notna()
    & (treemap_data["movieNm"].astype(str).str.strip() != "")
]

# 총 관객이 없는 경우 제외
treemap_data = treemap_data[
    treemap_data["total_audi"].notna()
]

# 트리맵
fig2 = px.treemap(
    treemap_data,
    path=["genre", "movieNm"],
    values="total_audi",
    title="장르별 영화 총 관객 트리맵"
)

fig2.update_traces(
    hovertemplate=(
        "<b>%{label}</b><br>"
        "총 관객: %{value:,.0f}명"
        "<extra></extra>"
    )
)

fig2.update_layout(
    height=700
)

st.plotly_chart(fig2, width="stretch")

# 설명 영역
st.markdown("---")
st.subheader("💡 이 그래프로 알 수 있는 것")
st.text_area(
    "설명 문장을 직접 작성해 보세요.",
    placeholder="예: 장르별로 어떤 영화가 많은 관객을 모았는지 비교할 수 있다.",
    key="graph2_description",
    height=80
)

st.markdown("---")
