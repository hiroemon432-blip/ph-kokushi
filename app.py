import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# --- Page Config ---
st.set_page_config(
    page_title="薬剤師国家試験 合格率可視化",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Styling ---
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    h1, h2, h3 {
        color: #1e3a8a;
    }
</style>
""", unsafe_allow_html=True)

# --- Data Loading ---
@st.cache_data
def load_data():
    file_path = "pharmacist_exam_data.csv"
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        return df
    else:
        return pd.DataFrame(columns=["Year", "University", "Category", "Applicants", "Passers", "PassRate"])

df = load_data()

# --- Sidebar ---
st.sidebar.title("🔍 検索・フィルター")

# Category Selector (Modes)
mode_options = ["全体（新卒＋既卒）", "新卒のみ", "既卒のみ"]
selected_mode = st.sidebar.radio("表示モードを選択", mode_options, index=0)

# Map UI mode to internal Category string
mode_to_cat = {
    "全体（新卒＋既卒）": "全体",
    "新卒のみ": "新卒",
    "既卒のみ": "既卒"
}
selected_category = mode_to_cat[selected_mode]

all_universities = sorted(df["University"].unique())
search_univ = st.sidebar.multiselect("大学名で検索 (複数選択可)", options=all_universities, default=[])

years = sorted(df["Year"].unique(), reverse=True)
if years:
    year_range = st.sidebar.select_slider("対象年 (年度)", options=sorted(years), value=(min(years), max(years)))
else:
    year_range = (0, 0)

sort_option = st.sidebar.selectbox("ソート順 (テーブル用)", ["合格率順 (降順)", "合格率順 (昇順)", "受験者数順", "学校名順"])

# --- Main Application ---
st.title("💊 薬剤師国家試験 大学別合格率推移")
st.write(f"直近6年分（2020年〜2025年）の大学別の合格状況（**{selected_mode}**）を可視化します。")

if df.empty:
    st.warning("データが見つかりません。`data_preparation.py`を実行してデータを生成してください。")
    st.stop()

# Filter data by Year and Category for global views
filtered_df = df[(df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])]
category_df = filtered_df[filtered_df["Category"] == selected_category]

# Metrics for top year
latest_year = max(years)
latest_cat_df = df[(df["Year"] == latest_year) & (df["Category"] == selected_category)]

if not latest_cat_df.empty:
    avg_pass_rate = latest_cat_df["PassRate"].mean()
    top_row = latest_cat_df.sort_values("PassRate", ascending=False).iloc[0]
    top_univ = top_row["University"]
    top_rate = top_row["PassRate"]

    col1, col2, col3 = st.columns(3)
    col1.metric(f"{latest_year}年 {selected_category}平均", f"{avg_pass_rate:.2f}%")
    col2.metric(f"{selected_category}第1位", top_univ)
    col3.metric(f"{selected_category}最高率", f"{top_rate:.2f}%")

st.divider()

# --- Trends Graph ---
st.header("📈 合格率推移の比較")
if search_univ:
    plot_df = category_df[category_df["University"].isin(search_univ)]
    if not plot_df.empty:
        fig = px.line(
            plot_df, 
            x="Year", 
            y="PassRate", 
            color="University",
            markers=True,
            title=f"選択した大学の{selected_mode}合格率推移",
            labels={"PassRate": "合格率 (%)", "Year": "年度", "University": "大学名"},
            template="plotly_white"
        )
        fig.update_layout(yaxis_range=[0, 105])
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("選択した範囲にデータがありません。")
else:
    st.info("左側のサイドバーから比較したい大学を選択してください。")

# --- Ranking display for a specific year ---
st.header(f"🏆 年次ランキング ({selected_mode})")
selected_rank_year = st.selectbox("ランキングを表示する年を選択", options=years)

# Get data for the selected year and category
rank_df = df[(df["Year"] == selected_rank_year) & (df["Category"] == selected_category)].sort_values("PassRate", ascending=False)
uni_order = rank_df["University"].tolist()

# Define Colors based on selection
colors = ["#f97316" if u in search_univ else "#cbd5e1" for u in uni_order]

fig_rank = go.Figure()

fig_rank.add_trace(go.Bar(
    y=uni_order,
    x=rank_df["PassRate"],
    orientation='h',
    marker_color=colors,
    text=rank_df["PassRate"].apply(lambda x: f"{x:.1f}%"),
    textposition='outside'
))

fig_rank.update_layout(
    title=f"{selected_rank_year}年度 {selected_mode} 合格率ランキング" + (" (選択した大学を強調)" if search_univ else ""),
    xaxis_title="合格率 (%)",
    yaxis_title="大学名",
    template="plotly_white",
    height=max(600, len(uni_order) * 30),
    xaxis_range=[0, 115],
    yaxis={'categoryorder':'array', 'categoryarray':uni_order[::-1]} # Reversed for top-to-bottom
)

st.plotly_chart(fig_rank, use_container_width=True)

# --- Data Table ---
st.header("📋 詳細データ一覧")

# Apply sorting to table
table_df = category_df.copy()
if sort_option == "合格率順 (降順)":
    table_df = table_df.sort_values(["Year", "PassRate"], ascending=[False, False])
elif sort_option == "合格率順 (昇順)":
    table_df = table_df.sort_values(["Year", "PassRate"], ascending=[False, True])
elif sort_option == "受験者数順":
    table_df = table_df.sort_values(["Year", "Applicants"], ascending=[False, False])
else:
    table_df = table_df.sort_values(["Year", "University"], ascending=[False, True])

st.dataframe(
    table_df[["Year", "University", "Category", "Applicants", "Passers", "PassRate"]],
    use_container_width=True,
    hide_index=True
)

st.sidebar.divider()
st.sidebar.info("データ提供: 厚生労働省 薬剤師国家試験 合格発表資料より抜粋・加工")
