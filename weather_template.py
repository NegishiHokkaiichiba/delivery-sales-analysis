import pandas as pd

# 1. 日付範囲の作成
dates = pd.date_range(start="2022-06-01", end="2025-05-20", freq="D")

# 2. テンプレート用 DataFrame 作成
df_weather = pd.DataFrame({
    "日付": dates,
    "平均気温 (℃)": pd.NA,
    "最高気温 (℃)": pd.NA,
    "最低気温 (℃)": pd.NA,
    "風速 (m/s)": pd.NA,
    "天候": pd.NA
})

# 3. Excel と CSV に保存
df_weather.to_excel("sapporo_weather_template.xlsx", index=False, sheet_name="Weather")
df_weather.to_csv("sapporo_weather_template.csv", index=False)
