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


# ============================================================
# 데이터 불러오기
# ============================================================

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

    # 숫자형 데이터 변환
    numeric_columns = [
        "first_scrn",
        "first_show",
        "first_week_audi",
        "total_audi",
        "days_in_top10"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
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

treemap_data = df[
    ["genre", "movieNm", "total_audi"]
].copy()

treemap_data = treemap_data[
    treemap_data["movieNm"].notna()
    & (treemap_data["movieNm"].astype(str).str.strip() != "")
]

treemap_data = treemap_data[
    treemap_data["total_audi"].notna()
]

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

st.markdown("---")
st.subheader("💡 이 그래프로 알 수 있는 것")
st.text_area(
    "설명 문장을 직접 작성해 보세요.",
    placeholder="예: 장르별로 어떤 영화가 많은 관객을 모았는지 비교할 수 있다.",
    key="graph2_description",
    height=80
)


# ============================================================
# 3. 총 관객 히스토그램
# ============================================================

st.markdown("---")
st.header("3. 영화별 총 관객 분포")

hist_data = df[
    ["movieNm", "total_audi"]
].dropna()

fig3 = px.histogram(
    hist_data,
    x="total_audi",
    nbins=20,
    title="영화별 총 관객 분포",
    labels={
        "total_audi": "총 관객",
        "count": "영화 편수"
    }
)

fig3.update_traces(
    hovertemplate=(
        "총 관객 구간: %{x}<br>"
        "영화 편수: %{y}편"
        "<extra></extra>"
    )
)

fig3.update_layout(
    height=550,
    xaxis_title="총 관객",
    yaxis_title="영화 편수"
)

st.plotly_chart(fig3, width="stretch")


# 가장 많이 몰려 있는 구간과 가장 관객이 많은 영화
if len(hist_data) > 0:

    bins = pd.cut(
        hist_data["total_audi"],
        bins=20,
        include_lowest=True
    )

    bin_counts = bins.value_counts().sort_index()
    most_common_bin = bin_counts.idxmax()

    max_audi_row = hist_data.loc[
        hist_data["total_audi"].idxmax()
    ]

    max_movie = max_audi_row["movieNm"]
    max_audi = max_audi_row["total_audi"]

    bin_start = most_common_bin.left
    bin_end = most_common_bin.right

    st.info(
        f"📊 **대부분의 영화가 몰려 있는 구간:** "
        f"{bin_start:,.0f}명 ~ {bin_end:,.0f}명\n\n"
        f"🏆 **가장 관객이 많은 영화:** "
        f"{max_movie} ({max_audi:,.0f}명)"
    )


st.markdown("---")
st.subheader("💡 이 그래프로 알 수 있는 것")
st.text_area(
    "설명 문장을 직접 작성해 보세요.",
    placeholder="예: 대부분의 영화가 어느 정도의 총 관객 구간에 몰려 있는지 알 수 있다.",
    key="graph3_description",
    height=80
)


# ============================================================
# 4. 개봉일 스크린수와 총 관객의 관계
# ============================================================

st.markdown("---")
st.header("4. 개봉일 스크린수와 총 관객의 관계")

scatter_data = df[
    ["movieNm", "genre", "first_scrn", "total_audi"]
].copy()

scatter_data = scatter_data.dropna(
    subset=["movieNm", "genre", "first_scrn", "total_audi"]
)

fig4 = px.scatter(
    scatter_data,
    x="first_scrn",
    y="total_audi",
    color="genre",
    hover_name="movieNm",
    title="개봉일 스크린수와 총 관객",
    labels={
        "first_scrn": "개봉일 스크린수",
        "total_audi": "총 관객",
        "genre": "장르"
    }
)

fig4.update_traces(
    marker=dict(
        size=10,
        opacity=0.75
    ),
    hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "개봉일 스크린수: %{x:,.0f}개<br>"
        "총 관객: %{y:,.0f}명"
        "<extra></extra>"
    )
)

fig4.update_layout(
    height=650,
    xaxis_title="개봉일 스크린수",
    yaxis_title="총 관객",
    legend_title="장르"
)

st.plotly_chart(fig4, width="stretch")

st.markdown("---")
st.subheader("💡 이 그래프로 알 수 있는 것")
st.text_area(
    "설명 문장을 직접 작성해 보세요.",
    placeholder="예: 개봉일 스크린수와 총 관객 사이에 어떤 관계가 있는지 살펴볼 수 있다.",
    key="graph4_description",
    height=80
)


# ============================================================
# 5. 장르별 총 관객 상자 그림
# ============================================================

st.markdown("---")
st.header("5. 장르별 총 관객 분포")

# 장르별 영화 편수 계산
genre_movie_count = (
    df["genre"]
    .value_counts()
)

# 영화가 10편 이상인 장르만 선택
selected_genres = genre_movie_count[
    genre_movie_count >= 10
].index

box_data = df[
    df["genre"].isin(selected_genres)
][
    ["genre", "movieNm", "total_audi"]
].dropna(
    subset=["genre", "movieNm", "total_audi"]
)

fig5 = px.box(
    box_data,
    x="genre",
    y="total_audi",
    points="outliers",
    hover_name="movieNm",
    title="영화가 10편 이상인 장르의 총 관객 분포",
    labels={
        "genre": "장르",
        "total_audi": "총 관객"
    }
)

fig5.update_traces(
    hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "총 관객: %{y:,.0f}명"
        "<extra></extra>"
    )
)

fig5.update_layout(
    height=650,
    xaxis_title="장르",
    yaxis_title="총 관객",
    yaxis_tickformat=","
)

st.plotly_chart(fig5, width="stretch")

# 설명 영역
st.markdown("---")
st.subheader("💡 이 그래프로 알 수 있는 것")
st.text_area(
    "설명 문장을 직접 작성해 보세요.",
    placeholder="예: 영화가 많은 장르에서 총 관객이 어떻게 분포하는지 비교할 수 있다.",
    key="graph5_description",
    height=80
)

st.markdown("---")
# ============================================================
# 6. 개봉일 스크린수와 총 관객의 관계 - 버블 그래프
# ============================================================

st.markdown("---")
st.header("6. 개봉일 스크린수와 총 관객의 관계 - 첫 주 관객 버블")

bubble_data = df[
    [
        "movieNm",
        "genre",
        "first_scrn",
        "total_audi",
        "first_week_audi"
    ]
].copy()

# 필요한 데이터가 없는 행 제외
bubble_data = bubble_data.dropna(
    subset=[
        "movieNm",
        "genre",
        "first_scrn",
        "total_audi",
        "first_week_audi"
    ]
)

# 첫 주 관객이 0 이하인 데이터 제외
bubble_data = bubble_data[
    bubble_data["first_week_audi"] > 0
]

fig6 = px.scatter(
    bubble_data,
    x="first_scrn",
    y="total_audi",
    color="genre",
    size="first_week_audi",
    size_max=45,
    hover_name="movieNm",
    title="개봉일 스크린수와 총 관객 - 첫 주 관객을 크기로 표현",
    labels={
        "first_scrn": "개봉일 스크린수",
        "total_audi": "총 관객",
        "first_week_audi": "첫 주 관객",
        "genre": "장르"
    }
)

fig6.update_traces(
    marker=dict(
        opacity=0.7
    ),
    hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "개봉일 스크린수: %{x:,.0f}개<br>"
        "총 관객: %{y:,.0f}명<br>"
        "첫 주 관객: %{marker.size:,.0f}명"
        "<extra></extra>"
    )
)

fig6.update_layout(
    height=700,
    xaxis_title="개봉일 스크린수",
    yaxis_title="총 관객",
    legend_title="장르"
)

st.plotly_chart(fig6, width="stretch")

# 설명 영역
st.markdown("---")
st.subheader("💡 이 그래프로 알 수 있는 것")
st.text_area(
    "설명 문장을 직접 작성해 보세요.",
    placeholder="예: 첫 주 관객이 많았던 영화가 어떤 위치에 분포하는지 살펴볼 수 있다.",
    key="graph6_description",
    height=80
)

st.markdown("---")
