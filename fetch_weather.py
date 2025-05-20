from datetime import datetime
from meteostat import Point, Daily
import pandas as pd

# ① 観測地点を指定（札幌市中央区の緯度・経度）
loc = Point(43.06206, 141.35444, 137)  # 標高 137m

# ② 期間を指定
start = datetime(2022, 6, 1)
end   = datetime(2025, 5, 20)

# ③ データ取得
data = Daily(loc, start, end)
df = data.fetch()

# ④ 必要な列を選択・名称変更
# ④ 必要な列を選択・名称変更
df = data.fetch()[['tavg', 'tmax', 'tmin', 'wspd', 'prcp']].rename(columns={
    'tavg':'平均気温 (℃)',
    'tmax':'最高気温 (℃)',
    'tmin':'最低気温 (℃)',
    'wspd':'風速 (m/s)',
    'prcp':'降水量 (mm)'
})

# ⑤ 小数を丸め
df = df.round(0)

# ⑥ 欠損値を 0 で埋めてから整数型に変換
df = df.fillna(0).astype(int)

# ⑦ 日付を列に戻し m/d 表示
df = df.reset_index().rename(columns={'time':'日付'})
df['日付'] = df['日付'].dt.strftime('%-m/%-d')

# ⑧ ファイル出力
df.to_excel('sapporo_weather.xlsx', index=False, sheet_name='Weather')
df.to_csv('sapporo_weather.csv', index=False)
