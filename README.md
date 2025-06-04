# delivery-sales-analysis

このプロジェクトは配達売上データを可視化する Streamlit アプリです。

## 使い方

1. 依存パッケージをインストールします。
   ```bash
   pip install -r requirements.txt
   ```
2. アプリを起動します。
   ```bash
   streamlit run app.py
   ```

売上データは `delivery_sales_analysis.xlsx` から読み込まれます。
気象情報や祝日の表示には `meteostat` と `jpholiday` パッケージが必要です。

`fetch_weather.py` を実行すると、
[meteostat](https://github.com/meteostat/meteostat) から天気データを取得して
ローカルファイルを更新できます。

## GitHub の基本的な使い方

ここでは GitHub を初めて使う方向けに、リポジトリの更新からプルリクエスト
（PR）の作成・マージまでの流れを簡単にまとめます。

1. **リポジトリを取得**する
   ```bash
   git clone <リポジトリURL>
   cd <リポジトリ名>
   ```
2. **ブランチを作成**して変更します。
   ```bash
   git checkout -b my-feature
   # ファイルを編集
   git add <変更したファイル>
   git commit -m "変更内容"
   git push origin my-feature
   ```
3. **Pull Request を作成**
   - GitHub 上のリポジトリページに表示される
     "Compare & pull request" ボタンをクリックします。
   - 変更内容の説明を書き、レビュワーを指定して PR を提出します。
4. **レビュー後にマージ**
   - レビューで指摘があれば修正をプッシュし直します。
   - 問題がなければ "Merge" ボタンを押してブランチを統合します。

詳しくは [GitHub Docs](https://docs.github.com/ja) もご覧ください。
