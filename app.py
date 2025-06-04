import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

st.set_page_config(page_title='売上ダッシュボード', layout='wide')

DEFAULT_FILE = 'delivery_sales_analysis.xlsx'
uploaded = st.sidebar.file_uploader('売上データ (Excel)', type='xlsx')
source = uploaded if uploaded is not None else DEFAULT_FILE

@st.cache_data
def load_data(path):
    df = pd.read_excel(path, sheet_name='Master', dtype={'日付': str})
    df['日付'] = pd.to_datetime(df['日付'], errors='coerce')
    df = df.dropna(subset=['日付'])
    df['日付'] = df['日付'].dt.date
    return df

try:
    data = load_data(source)
except Exception as e:
    st.error(f'データ読み込みに失敗しました: {e}')
    st.stop()

# ---- フィルター ----
platforms = sorted({c.split('_')[0] for c in data.columns if c.endswith('_税込')})
selected_platform = st.selectbox('プラットフォーム', ['全て'] + platforms)
start_d, end_d = st.date_input('日付範囲', [data['日付'].min(), data['日付'].max()])

filtered = data[(data['日付'] >= start_d) & (data['日付'] <= end_d)]

# ---- 日別売上推移 ----
if selected_platform == '全て':
    cols = [f'{p}_税込' for p in platforms if f'{p}_税込' in filtered]
    filtered['売上'] = filtered[cols].sum(axis=1)
else:
    col = f'{selected_platform}_税込'
    filtered['売上'] = filtered[col]

daily = filtered.groupby('日付')['売上'].sum().reset_index()
st.header('📈 日別売上推移')
fig_daily = px.line(daily, x='日付', y='売上', markers=True)
st.plotly_chart(fig_daily, use_container_width=True)

# ---- プラットフォーム別売上構成 ----
composition = {}
for p in platforms:
    col = f'{p}_税込'
    if col in filtered:
        composition[p] = int(filtered[col].sum())
comp_df = pd.DataFrame(list(composition.items()), columns=['プラットフォーム', '売上'])
st.header('📊 プラットフォーム別売上構成')
fig_comp = px.bar(comp_df, x='プラットフォーム', y='売上', color='プラットフォーム',
                  color_discrete_map={'Uber':'green','Wolt':'skyblue','menu':'red'})
st.plotly_chart(fig_comp, use_container_width=True)

# ---- カテゴリ別売上ランキング ----
if 'カテゴリ' in filtered.columns:
    cat_df = filtered.groupby('カテゴリ')['売上'].sum().reset_index()
    cat_df = cat_df.sort_values('売上', ascending=False).head(10)
    st.header('🧾 カテゴリ別売上ランキング')
    fig_cat = px.bar(cat_df, x='カテゴリ', y='売上')
    st.plotly_chart(fig_cat, use_container_width=True)

# ---- 特記事項 ----
NOTES = [
    '5/1：チラシキャンペーン開始（惣菜カテゴリー）',
    '5/3：雨天により売上減少',
    '5/5：Uber限定20%割引セール'
]

st.header('📝 特記事項・キャンペーン')
for n in NOTES:
    st.write('-', n)
