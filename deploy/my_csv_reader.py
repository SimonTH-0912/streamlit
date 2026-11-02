from __future__ import annotations

from io import BytesIO

import pandas as pd
import streamlit as st


st.set_page_config(page_title="DataLens", page_icon="📊", layout="wide")
st.title("📊 DataLens")
st.caption("CSV 파일을 업로드하면 데이터 품질을 확인하고, 필터링하고, 그래프로 탐색할 수 있습니다.")


@st.cache_data(show_spinner=True)
def load_csv(file_bytes: bytes, separator: str) -> tuple[pd.DataFrame, str]:
    """자주 쓰이는 한글/영문 인코딩을 차례로 시도해 CSV를 읽습니다."""
    errors: list[str] = []
    for encoding in ("utf-8-sig", "utf-8", "cp949", "euc-kr"):
        try:
            frame = pd.read_csv(BytesIO(file_bytes), sep=separator, encoding=encoding)
            return frame, encoding
        except (UnicodeDecodeError, UnicodeError) as error:
            errors.append(f"{encoding}: {error}")
    raise ValueError("지원하는 인코딩으로 파일을 읽지 못했습니다. " + " | ".join(errors))


def create_summary(df: pd.DataFrame) -> list[str]:
    rows, columns = df.shape
    missing = df.isna().sum()
    numeric = df.select_dtypes(include="number").columns.tolist()
    categorical = df.select_dtypes(exclude="number").columns.tolist()
    summaries = [f"데이터는 {rows:,}개 행과 {columns:,}개 열로 구성되어 있습니다."]

    if int(missing.sum()) == 0:
        summaries.append("결측값이 없습니다.")
    else:
        name = str(missing.idxmax())
        count = int(missing.max())
        summaries.append(f"결측값은 총 {int(missing.sum()):,}개이며, '{name}' 열에 가장 많습니다({count:,}개).")

    summaries.append(f"숫자형 열은 {len(numeric)}개, 그 외 열은 {len(categorical)}개입니다.")

    if len(numeric) >= 2:
        corr = df[numeric].corr(numeric_only=True)
        upper_pairs = corr.where(
            pd.DataFrame(
                [[column_index > row_index for column_index in range(len(corr.columns))]
                 for row_index in range(len(corr.index))],
                index=corr.index,
                columns=corr.columns,
            )
        ).stack().dropna()
        if not upper_pairs.empty:
            first, second = upper_pairs.abs().idxmax()
            value = corr.loc[first, second]
            summaries.append(f"가장 강한 선형 관계는 '{first}'와 '{second}' 사이이며 상관계수는 {value:.2f}입니다.")
    return summaries


def apply_filters(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    filtered = df.copy()
    for column in columns:
        series = filtered[column]
        if pd.api.types.is_numeric_dtype(series):
            valid = series.dropna()
            if valid.empty:
                continue
            low, high = float(valid.min()), float(valid.max())
            if low == high:
                st.sidebar.caption(f"{column}: 모든 값이 {low:g}")
                continue
            selected = st.sidebar.slider(column, low, high, (low, high))
            filtered = filtered[filtered[column].between(*selected) | filtered[column].isna()]
        else:
            choices = sorted(series.dropna().astype(str).unique().tolist())
            if len(choices) > 200:
                query = st.sidebar.text_input(f"{column} 포함 검색")
                if query:
                    filtered = filtered[filtered[column].astype(str).str.contains(query, case=False, na=False)]
            else:
                selected = st.sidebar.multiselect(column, choices)
                if selected:
                    filtered = filtered[filtered[column].astype(str).isin(selected)]
    return filtered


with st.sidebar:
    st.header("파일 및 필터")
    uploaded_file = st.file_uploader("CSV 파일 업로드", type=["csv"])
    use_sample = st.checkbox("샘플 데이터로 시작", value=False, disabled=uploaded_file is not None)
    separator_label = st.selectbox("구분자", ["쉼표 (,)", "세미콜론 (;)", "탭 (Tab)", "파이프 (|)"])

if uploaded_file is None and not use_sample:
    st.info("왼쪽 사이드바에서 CSV 파일을 업로드하거나 샘플 데이터로 시작해 주세요.")
    st.stop()

separator = {"쉼표 (,)": ",", "세미콜론 (;)": ";", "탭 (Tab)": "\t", "파이프 (|)": "|"}[separator_label]
try:
    if uploaded_file is not None:
        df, detected_encoding = load_csv(uploaded_file.getvalue(), separator)
    else:
        sample = "날짜,매장,방문자,매출\n월요일,강남,120,560000\n화요일,강남,145,680000\n수요일,홍대,90,420000\n목요일,홍대,110,510000\n금요일,강남,170,790000\n"
        df, detected_encoding = load_csv(sample.encode("utf-8"), ",")
except Exception as error:
    st.error(f"CSV 파일을 읽지 못했습니다: {error}")
    st.stop()

if df.empty:
    st.warning("업로드한 CSV 파일에 데이터가 없습니다.")
    st.stop()

if uploaded_file is None:
    st.caption("연습용 가상 데이터입니다. 실제 매출 자료가 아닙니다.")

with st.sidebar:
    st.success(f"{detected_encoding} 인코딩으로 읽었습니다.")
    filter_columns = st.multiselect("필터로 사용할 열", df.columns.tolist())
    filtered_df = apply_filters(df, filter_columns)
    st.caption(f"필터 결과: {len(filtered_df):,} / {len(df):,}행")

if filtered_df.empty:
    st.warning("현재 필터 조건에 맞는 행이 없습니다. 필터를 변경하거나 해제해 주세요.")

tab_overview, tab_quality, tab_chart, tab_correlation = st.tabs(
    ["개요", "데이터 품질", "그래프", "상관관계"]
)

with tab_overview:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("행", f"{len(filtered_df):,}", delta=f"전체 {len(df):,}")
    col2.metric("열", f"{df.shape[1]:,}")
    col3.metric("결측값", f"{int(filtered_df.isna().sum().sum()):,}")
    col4.metric("중복 행", f"{int(filtered_df.duplicated().sum()):,}")

    st.subheader("자동 분석 요약")
    for sentence in create_summary(filtered_df):
        st.markdown(f"- {sentence}")

    st.subheader("데이터 미리보기")
    preview_count = st.slider("표시할 행 수", 5, min(200, max(5, len(filtered_df))), min(20, max(5, len(filtered_df))))
    st.dataframe(filtered_df.head(preview_count), use_container_width=True, hide_index=True)
    st.download_button(
        "필터 결과 CSV 다운로드",
        filtered_df.to_csv(index=False).encode("utf-8-sig"),
        file_name="filtered_data.csv",
        mime="text/csv",
    )

with tab_quality:
    info = pd.DataFrame({
        "열 이름": df.columns,
        "자료형": df.dtypes.astype(str).values,
        "결측값": df.isna().sum().values,
        "결측률(%)": (df.isna().mean().values * 100).round(2),
        "고유값": df.nunique(dropna=True).values,
    })
    st.dataframe(info, use_container_width=True, hide_index=True)
    numeric_df = filtered_df.select_dtypes(include="number")
    if numeric_df.empty:
        st.info("숫자형 열이 없어 기술 통계를 표시할 수 없습니다.")
    else:
        st.subheader("숫자형 기술 통계")
        st.dataframe(numeric_df.describe().T, use_container_width=True)

with tab_chart:
    numeric_columns = filtered_df.select_dtypes(include="number").columns.tolist()
    chart_type = st.selectbox("그래프 종류", ["막대", "선", "영역", "산점도"])
    if chart_type == "산점도":
        if len(numeric_columns) < 2:
            st.info("산점도에는 숫자형 열이 2개 이상 필요합니다.")
        else:
            x_column = st.selectbox("X축", numeric_columns)
            y_column = st.selectbox("Y축", numeric_columns, index=1)
            color_options = ["사용 안 함"] + df.columns.tolist()
            color_column = st.selectbox("색상 구분", color_options)
            kwargs = {} if color_column == "사용 안 함" else {"color": color_column}
            st.scatter_chart(filtered_df, x=x_column, y=y_column, **kwargs)
    else:
        selected_columns = st.multiselect("표시할 숫자형 열", numeric_columns, default=numeric_columns[:1])
        if not selected_columns:
            st.info("그래프에 표시할 숫자형 열을 선택해 주세요.")
        else:
            chart_data = filtered_df[selected_columns]
            {"막대": st.bar_chart, "선": st.line_chart, "영역": st.area_chart}[chart_type](chart_data)

with tab_correlation:
    numeric_df = filtered_df.select_dtypes(include="number")
    if numeric_df.shape[1] < 2:
        st.info("상관관계 분석에는 숫자형 열이 2개 이상 필요합니다.")
    else:
        st.caption("1에 가까울수록 같은 방향, -1에 가까울수록 반대 방향의 선형 관계가 강합니다.")
        st.dataframe(numeric_df.corr().round(3), use_container_width=True)
