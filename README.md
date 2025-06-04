# delivery-sales-analysis

このプロジェクトは配達売上データを可視化する Streamlit アプリです。

`dashboard_demo.html` にシンプルなダッシュボードのサンプルも用意しました。ブラウザで開くだけでレイアウトを確認できます。

## アプリの特徴

- サイドバーの設定から **月単位** または **期間指定** の分析が可能です。
- 指標を 1 つ選ぶと「概要」と「日別推移」の 2 つのタブで結果を確認できます（"全てを表示" 選択時は日別推移タブで指標を選び直してください）。
- Uber Eats は緑、Wolt は水色で表示され、比較もしやすくなっています。
- 月を 2 つ選択すると差分や増減率を自動計算して表示します。
- サイドバーから Excel ファイルをアップロードすると独自の売上データで分析できます。

## 必要条件

- Windows 10/11
- Python 3.8 以上（推奨）
- PowerShell または コマンドプロンプト

## 使い方

1.仮想環境 .venv を作成
   ```bash
   py -m venv .venv
   ```
2.仮想環境を有効化（PowerShell）
  ```bash
   .\.venv\Scripts\Activate.ps1
  ``` 
3. 依存パッケージをインストールします。
   ```bash
   py -m pip install -r requirements.txt
   ```
4. アプリを起動します。
   ```bash
   streamlit run app.py
   ```
   ブラウザが開いたら、ページ左の「設定」パネルで分析モードや指標を選択します。
   月単位の分析では先月比・前年同月比もワンクリックで比較可能です。
   期間指定モードではカレンダーから自由に日付範囲を選べます。

デフォルトでは `delivery_sales_analysis.xlsx` を読み込みますが、アップロードした Excel ファイルを使用することも可能です。
天気の表示には `meteostat` パッケージが必要です。

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
