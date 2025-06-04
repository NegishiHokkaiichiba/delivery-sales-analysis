import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import datetime

# Optional imports
try:
    from meteostat import Point, Daily
except ImportError:
    Point = None
    Daily = None
# --- アプリ設定: ワイドレイアウト ---
st.set_page_config(layout='wide')

# --- データファイル選択 ---
DEFAULT_FILE = 'delivery_sales_analysis.xlsx'
uploaded = st.sidebar.file_uploader('売上データ (Excel)', type='xlsx')
data_source = uploaded if uploaded is not None else DEFAULT_FILE

if Point is None or Daily is None:
    st.sidebar.info('天候・気温を表示するには meteostat パッケージをインストールしてください。')

# --- 1. データ読み込みと前処理 ---
@st.cache_data
def load_master(source):
    df = pd.read_excel(source, sheet_name='Master', dtype={'日付': str})
    # 日付を正しく datetime 型に変換し時刻を除去
    df['日付'] = pd.to_datetime(df['日付'], errors='coerce').dt.normalize()
    df = df.dropna(subset=['日付'])
    df['Month'] = df['日付'].dt.to_period('M').astype(str)
    return df

try:
    master = load_master(data_source)
except FileNotFoundError:
    st.error(f"データファイル {data_source} が見つかりません")
    st.stop()

# --- 2. 有効月選択（昇順） ---
metric_suffix_map = {
    '店舗売上（税抜）': '_税抜',
    '店舗売上（税込）': '_税込',
    'アプリ売上':    '_アプリ売上',
    '件数':         '_件数'
}
metric_cols = [c for c in master.columns if any(suffix in c for suffix in metric_suffix_map.values())]

def get_valid_months(df):
    # 売上または件数が1件以上ある月のみ
    months = [m for m, grp in df.groupby('Month') if any(grp[col].sum() > 0 for col in metric_cols)]
    return sorted(months)

valid_months = get_valid_months(master)
if 'selected_month' not in st.session_state:
    st.session_state.selected_month = valid_months[-1]
selected_month = st.sidebar.selectbox(
    '月を選択', valid_months,
    index=valid_months.index(st.session_state.selected_month),
    key='selected_month'
)

compare_options = ['(比較しない)'] + valid_months
if 'compare_month' not in st.session_state:
    default_idx = len(compare_options) - 2 if len(compare_options) > 2 else 0
    st.session_state.compare_month = compare_options[default_idx]
compare_month = st.sidebar.selectbox(
    '比較月', compare_options,
    index=compare_options.index(st.session_state.compare_month),
    key='compare_month'
)

year, mon = selected_month.split('-')
jmonth = f"{year}年{int(mon)}月"
if compare_month != '(比較しない)':
    c_year, c_mon = compare_month.split('-')
    jmonth_cmp = f"{c_year}年{int(c_mon)}月"
else:
    jmonth_cmp = ''

# --- 3. 指標選択 ---
metric_options = ['全てを表示'] + list(metric_suffix_map.keys())
if 'metric_label' not in st.session_state:
    st.session_state.metric_label = metric_options[1]
for m in metric_options:
    if st.sidebar.button(m):
        st.session_state.metric_label = m
metric_label = st.session_state.metric_label

# 色マップ
color_map = {'Uber':'green', 'Wolt':'skyblue', 'menu':'red'}

# --- 4. データ抽出 ---
df_sel = master[master['Month'] == selected_month]
df_cmp = master[master['Month'] == compare_month] if compare_month != '(比較しない)' else None
platforms = sorted({col.split('_')[0] for col in metric_cols})
# menuが適用外の月は除外
if selected_month > '2024-10' and 'menu' in platforms:
    platforms.remove('menu')

# --- 5. タイトル ---
title = f"{jmonth} {metric_label} 分析"
if jmonth_cmp:
    title = f"{jmonth} vs {jmonth_cmp} {metric_label} 比較"
st.title(title)

# --- 6. 全指標表示 ---
if metric_label == '全てを表示':
    def summarize(df):
        records = []
        for plat in platforms:
            rec = {'プラットフォーム': plat}
            for lbl, suf in metric_suffix_map.items():
                col = f"{plat}{suf}"
                rec[lbl] = int(df[col].sum()) if col in df else 0
            records.append(rec)
        return pd.DataFrame(records).set_index('プラットフォーム')

    df_all = summarize(df_sel)
    st.header('全指標一覧')
    st.table(df_all)

    if df_cmp is not None:
        df_cmp_all = summarize(df_cmp)
        diff = df_cmp_all - df_all
        growth = (df_cmp_all / df_all.replace(0, pd.NA) - 1).fillna(0)
        cmp_table = pd.concat([
            df_all.add_suffix(f'({jmonth})'),
            df_cmp_all.add_suffix(f'({jmonth_cmp})'),
            diff.add_suffix(' 差分'),
            (growth*100).round(1).add_suffix(' 増減%')
        ], axis=1)
        st.subheader('比較表')
        st.table(cmp_table)

        graph_records = []
        for plat in platforms:
            for lbl in metric_suffix_map.keys():
                graph_records.append({'プラットフォーム': plat, '指標': lbl, '月': jmonth, '値': df_all.loc[plat, lbl]})
                graph_records.append({'プラットフォーム': plat, '指標': lbl, '月': jmonth_cmp, '値': df_cmp_all.loc[plat, lbl]})
        df_graph = pd.DataFrame(graph_records)
    else:
        df_graph = df_all.reset_index().melt(id_vars='プラットフォーム', var_name='指標', value_name='値')
        df_graph['月'] = jmonth

    fig_all = px.bar(
        df_graph,
        x='プラットフォーム',
        y='値',
        color='月',
        barmode='group',
        facet_col='指標',
        category_orders={'月': [jmonth, jmonth_cmp] if jmonth_cmp else [jmonth]},
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig_all.update_layout(hovermode='x unified')
    st.plotly_chart(fig_all, use_container_width=True)

# --- 7. 単一指標表示 ---
else:
    suf = metric_suffix_map[metric_label]
    summary = []
    for plat in platforms:
        col = f"{plat}{suf}"
        if col in df_sel.columns:
            v = int(df_sel[col].sum())
            if v > 0:
                summary.append({'プラットフォーム': plat, metric_label: v})
    df_summary = pd.DataFrame(summary)

    if df_cmp is not None:
        summary_cmp = []
        for plat in platforms:
            col = f"{plat}{suf}"
            if col in df_cmp.columns:
                v = int(df_cmp[col].sum())
                if v > 0:
                    summary_cmp.append({'プラットフォーム': plat, metric_label: v})
        df_cmp_summary = pd.DataFrame(summary_cmp)
        df_cmp_summary = df_cmp_summary.set_index('プラットフォーム')
        df_summary = df_summary.set_index('プラットフォーム')
        diff = df_cmp_summary - df_summary
        growth = (df_cmp_summary / df_summary.replace(0, pd.NA) - 1).fillna(0)
        cmp_table = pd.concat([
            df_summary.add_suffix(f'({jmonth})'),
            df_cmp_summary.add_suffix(f'({jmonth_cmp})'),
            diff.add_suffix(' 差分'),
            (growth*100).round(1).add_suffix(' 増減%')
        ], axis=1)
        st.subheader('比較表')
        st.table(cmp_table)

        df_graph = pd.concat([
            df_summary.reset_index().assign(月=jmonth),
            df_cmp_summary.reset_index().assign(月=jmonth_cmp)
        ])
        fig1 = px.bar(
            df_graph, x='プラットフォーム', y=metric_label, color='月',
            barmode='group', color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig1, use_container_width=True)
    else:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader('構成比')
            fig1 = px.pie(
                df_summary, names='プラットフォーム', values=metric_label,
                color='プラットフォーム', color_discrete_map=color_map
            )
            fig1.update_traces(textinfo='percent+label', hoverlabel=dict(font_size=16))
            st.plotly_chart(fig1, use_container_width=True)
        with c2:
            st.subheader('数値')
            st.table(df_summary.set_index('プラットフォーム'))

    # --- 8. 日別推移 ---
    st.subheader('日別推移（曜日・気温・天候）')
    val_cols = [f"{plat}{suf}" for plat in platforms]
    pivot = df_sel.groupby('日付')[val_cols].sum().reset_index()
    # 曜日
    pivot['曜日'] = pivot['日付'].dt.weekday.map({0:'月',1:'火',2:'水',3:'木',4:'金',5:'土',6:'日'})
    # 日付 m/d
    fmt = '%#m/%#d' if sys.platform.startswith('win') else '%-m/%-d'
    pivot['日付'] = pivot['日付'].dt.strftime(fmt)
    # カラムリネームプラットフォーム名のみ
    rename_map = {col: col.replace(suf, '') for col in val_cols}
    merged = pivot.rename(columns=rename_map)
    # 天候・気温列初期化
    merged[['天候','最高気温','最低気温','平均気温']] = ''

    # 気象
    if Point and Daily:
        start = datetime.datetime(int(year), int(mon), 1)
        end = (start + pd.offsets.MonthEnd(1)).to_pydatetime()
        loc = Point(43.06417, 141.34694)
        try:
            weather = Daily(loc, start, end).fetch()[['tmin','tmax','tavg','prcp']].reset_index()
            weather['日付'] = weather['time'].dt.strftime(fmt)
            w = weather.set_index('日付')
            merged = merged.set_index('日付')
            merged['天候'] = w['prcp'].apply(lambda x: '☔' if x>0 else '☀️').reindex(merged.index, fill_value='')
            for src, tgt in [('tmax','最高気温'),('tmin','最低気温'),('tavg','平均気温')]:
                merged[tgt] = w[src].round().astype('Int64').reindex(merged.index, fill_value='')
            merged = merged.reset_index()
        except:
            merged = merged.reset_index()

    # テーブル表示
    display_cols = ['日付','曜日'] + list(rename_map.values()) + ['天候','最高気温','最低気温','平均気温']
    table_df = merged.reindex(columns=display_cols, fill_value='')
    # 売上系整数化
    for col in rename_map.values():
        if col in table_df:
            table_df[col] = table_df[col].astype(int)
    # ハイライト最大最小
    styled = table_df.style.apply(
        lambda col: ['background-color: yellow' if v==col.max() else 'background-color: lightblue' if v==col.min() else '' for v in col]
        if col.name in rename_map.values() else ['' for _ in col], axis=0
    )
    # インデックス非表示
    styled = styled.hide(axis='index')
    st.dataframe(styled, use_container_width=True)

    # 折れ線グラフ
    df_line = table_df.melt(id_vars=['日付'], value_vars=list(rename_map.values()), var_name='プラットフォーム', value_name=metric_label)
    fig2 = px.line(
        df_line, x='日付', y=metric_label, color='プラットフォーム',
        color_discrete_map=color_map, markers=True
    )
    fig2.update_layout(xaxis_title='日付', yaxis_title=metric_label, hoverlabel=dict(font_size=16))
    st.plotly_chart(fig2, use_container_width=True)
