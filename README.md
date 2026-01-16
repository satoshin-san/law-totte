# 🐶 法令、とってきました。 (Law-Totte)

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Visitor Count](https://visitor-badge.laobi.icu/badge?page_id=satoshin_law_totte_app_readme&right_color=orange&left_text=Visitors)

<div align="center">
  <h3>
    <a href="https://law-totte.streamlit.app/">
      🚀 デモアプリを試す (Launch App)
    </a>
  </h3>
</div>

<p align="center">
  <img src="images/banner.png" width="100%" alt="法令、とってきました。バナー">
</p>

**「AIのための法令あつめ、わたしが代わりにやっておきます。」**

e-Gov法令APIを活用し、日本の法令データを取得して **AI（NotebookLMやChatGPT等）が読みやすいMarkdown形式** に変換・ダウンロードできるWebアプリケーションです。

## 📖 概要 (Overview)

建築実務や法務確認において、法令の条文をAIに分析させたい場面が増えています。しかし、e-Govの生データ（XML）やWebコピーでは、条文の階層構造が崩れてしまい、AIが正しく理解できないことがあります。

このアプリは、**「AIに読ませるための最適なデータセット」** を、面倒なコピペなしで誰でも簡単に作成できるツールです。

## ✨ 主な機能 (Features)

1.  **公式分類からのスマート検索** 🏛️
    * 国の「事項別分類コード（50種類）」に準拠。「建築・住宅」「労働」「環境保全」など、実務に即したカテゴリから探せます。
    * 「略称（例：建基法）」や「読み仮名」でも検索可能です。

2.  **ショッピングカート方式のUI** 🛒
    * 検索ボックスで選んだ法令を、下のリストに次々と追加する「カート方式」を採用。
    * 検索窓が埋まることなく、大量の法令をスムーズに選択・管理できます。

3.  **AI最適化 Markdown出力** 🤖
    * 複雑な法令XML（編・章・節・条・項・号）を、Markdownの階層構造（# ヘッダー）に美しく変換。
    * **表データ（別表）** もテキストとして抽出。
    * **画像データ（外字・図）** も自動で解凍・埋め込み処理。

4.  **便利なリスト管理** 📂
    * 「いつものセット」をJSONファイルとして保存・読込可能。
    * プロジェクトごとに必要な法令セットを瞬時に復元できます。

## 🚀 使い方 (Usage)

### ローカル環境での実行

1.  **リポジトリをクローン**
    ```bash
    git clone [https://github.com/あなたのユーザー名/law-totte.git](https://github.com/あなたのユーザー名/law-totte.git)
    cd law-totte
    ```

2.  **必要なライブラリをインストール**
    ```bash
    pip install -r requirements.txt
    ```

3.  **アプリを起動**
    ```bash
    streamlit run app.py
    ```

4.  ブラウザで `http://localhost:8501` にアクセスしてください。

## 📂 ディレクトリ構成

```text
law-totte/
├── app.py                # アプリケーション本体
├── requirements.txt      # 依存ライブラリ
├── images/               # 画像リソース
│   └── banner.png        # バナー画像
├── docs/                 # ドキュメント類
└── README.md             # このファイル
