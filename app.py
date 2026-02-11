import streamlit as st
import requests
import pandas as pd
import json
import io
import zipfile
import base64
import re
import xml.etree.ElementTree as ET
from datetime import datetime

# ==========================================
# 0. プリセット法令リスト (建築基準法関係規定)
# ==========================================
PRESET_CONSTRUCTION_LAWS = [
    # --- 1. 建築・都市計画の基本 ---
    "建築基準法", "建築基準法施行令", "建築基準法施行規則",
    "都市計画法", "都市計画法施行令", "都市計画法施行規則",
    "都市緑地法", "都市緑地法施行令", "都市緑地法施行規則",
    "流通業務市街地の整備に関する法律", "流通業務市街地の整備に関する法律施行令", "流通業務市街地の整備に関する法律施行規則",
    "宅地造成及び特定盛土等規制法", "宅地造成及び特定盛土等規制法施行令", "宅地造成及び特定盛土等規制法施行規則",
    "景観法", "景観法施行令", "景観法施行規則",
    # --- 2. 住宅・性能評価 ---
    "住宅の品質確保の促進等に関する法律", "住宅の品質確保の促進等に関する法律施行令", "住宅の品質確保の促進等に関する法律施行規則",
    "長期優良住宅の普及の促進に関する法律", "長期優良住宅の普及の促進に関する法律施行令", "長期優良住宅の普及の促進に関する法律施行規則",
    "住宅宿泊事業法", "住宅宿泊事業法施行令", "住宅宿泊事業法施行規則",
    # --- 3. 省エネ・リサイクル ---
    "建築物のエネルギー消費性能の向上等に関する法律", "建築物のエネルギー消費性能の向上等に関する法律施行令", "建築物のエネルギー消費性能の向上等に関する法律施行規則",
    "建設工事に係る資材の再資源化等に関する法律", "建設工事に係る資材の再資源化等に関する法律施行令", "建設工事に係る資材の再資源化等に関する法律施行規則",
    # --- 4. 消防・危険物・産業保安 ---
    "消防法", "消防法施行令", "消防法施行規則",
    "液化石油ガスの保安の確保及び取引の適正化に関する法律", "液化石油ガスの保安の確保及び取引の適正化に関する法律施行令", "液化石油ガスの保安の確保及び取引の適正化に関する法律施行規則",
    "高圧ガス保安法", "高圧ガス保安法施行令",
    "ガス事業法", "ガス事業法施行令", "ガス事業法施行規則",
    "労働安全衛生法", "労働安全衛生法施行令", "労働安全衛生規則",
    # --- 5. 水・衛生・環境 ---
    "水道法", "水道法施行令", "水道法施行規則",
    "下水道法", "下水道法施行令", "下水道法施行規則",
    "浄化槽法", "浄化槽法施行令", "環境省関係浄化槽法施行規則",
    "建築物における衛生的環境の確保に関する法律", "建築物における衛生的環境の確保に関する法律施行令", "建築物における衛生的環境の確保に関する法律施行規則",
    "特定都市河川浸水被害対策法", "特定都市河川浸水被害対策法施行令", "特定都市河川浸水被害対策法施行規則",
    # --- 6. 交通・駐車場・港湾・空港 ---
    "駐車場法", "駐車場法施行令", "駐車場法施行規則",
    "自転車の安全利用の促進及び自転車等の駐車対策の総合的推進に関する法律", "自転車の安全利用の促進及び自転車等の駐車対策の総合的推進に関する法律施行令", "自転車の安全利用の促進及び自転車等の駐車対策の総合的推進に関する法律施行規則",
    "港湾法", "港湾法施行令", "港湾法施行規則",
    "特定空港周辺航空機騒音対策特別措置法", "特定空港周辺航空機騒音対策特別措置法施行令", "特定空港周辺航空機騒音対策特別措置法施行規則",
    # --- 7. 福祉・その他 ---
    "高齢者、障害者等の移動等の円滑化の促進に関する法律", "高齢者、障害者等の移動等の円滑化の促進に関する法律施行令", "高齢者、障害者等の移動等の円滑化の促進に関する法律施行規則",
    # --- 8. 営業許可関連 ---
    "旅館業法", "旅館業法施行令", "旅館業法施行規則",
    "興行場法", "興行場法施行規則",
]

# ==========================================
# 1. アプリの設定とデザイン (UI/UX)
# ==========================================
st.set_page_config(
    page_title="法令、とってきました。",
    page_icon="🐶",
    layout="centered"
)

# 優しいデザインにするためのカスタムCSS（ダークモード完全対策版）
st.markdown("""
    <style>
    /* --- 1. 全体の配色設定 --- */
    .stApp { 
        background-color: #FFFBF0;
        color: #333333 !important;
    }
    
    /* --- 2. 文字色固定 --- */
    h1, h2, h3, h4, h5, h6, p, div, span, label, li {
        color: #333333;
        font-family: "Hiragino Maru Gothic Pro", "Yu Gothic UI", sans-serif;
    }
    
    /* --- 3. 入力ボックス --- */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] > div, .stMultiSelect div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: #333333 !important;
        border-radius: 12px;
        border: 1px solid #E0E0E0;
    }

    /* --- ドロップダウンリスト --- */
    div[data-baseweb="popover"], div[data-baseweb="menu"] {
        background-color: #FFFFFF !important;
    }
    ul[data-testid="stSelectboxVirtualDropdown"] li, 
    ul[data-testid="stSelectboxVirtualDropdown"] div {
        background-color: #FFFFFF !important;
        color: #333333 !important;
    }
    ul[data-testid="stSelectboxVirtualDropdown"] li:hover {
        background-color: #FFF3E0 !important;
    }
    ul[data-testid="stSelectboxVirtualDropdown"] li[aria-selected="true"] {
        background-color: #FFE0B2 !important;
        color: #333333 !important;
    }
    
    /* --- 4. ボタンのデザイン --- */
    div.stButton > button {
        background-color: #FF8C00; 
        color: white !important; 
        border-radius: 12px; 
        border: none; 
        padding: 10px 24px; 
        font-weight: bold;
    }
    div.stButton > button:hover { 
        background-color: #E67E22; 
        color: white !important; 
    }
    
    /* 削除ボタン */
    div[data-testid="column"] button {
        background-color: #FF6B6B; 
        color: white !important; 
        border-radius: 50%; 
        width: 30px; 
        height: 30px; 
        padding: 0;
    }
    
    /* --- 5. リストカードのデザイン --- */
    .law-card {
        background-color: white;
        padding: 10px 15px;
        border-radius: 8px;
        margin-bottom: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        display: flex;
        align-items: center;
        color: #333333 !important;
    }
    
    .stMultiSelect, .stTextInput, .stSelectbox { border-radius: 12px; }
    .stMultiSelect span { font-family: "Hiragino Kaku Gothic ProN", sans-serif; }
    
    /* --- Step 2の選択タグの色修正 --- */
    span[data-baseweb="tag"] {
        background-color: #FFF3E0 !important;
        border: 1px solid #FFB74D !important;
    }
    span[data-baseweb="tag"] span {
        color: #333333 !important;
    }
    span[data-baseweb="tag"] svg {
        fill: #FF8C00 !important;
        color: #FF8C00 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 定数・設定
# ==========================================
API_V1_LIST_URL = "https://laws.e-gov.go.jp/api/1/lawlists/1"
API_V2_LIST_URL = "https://laws.e-gov.go.jp/api/2/laws"
API_V1_DETAILS_URL = "https://laws.e-gov.go.jp/api/1/lawdata"

OFFICIAL_CATEGORY_MAP = {
    "憲法": "001", "刑事": "002", "財務通則": "003", "水産業": "004", "観光": "005",
    "国会": "006", "警察": "007", "国有財産": "008", "鉱業": "009", "郵務": "010",
    "行政組織": "011", "消防": "012", "国税": "013", "工業": "014", "電気通信": "015",
    "国家公務員": "016", "国土開発": "017", "事業": "018", "商業": "019", "労働": "020",
    "行政手続": "021", "土地": "022", "国債": "023", "金融・保険": "024", "環境保全": "025",
    "統計": "026", "都市計画": "027", "教育": "028", "外国為替・貿易": "029", "厚生": "030",
    "地方自治": "031", "道路": "032", "文化": "033", "陸運": "034", "社会福祉": "035",
    "地方財政": "036", "河川": "037", "産業通則": "038", "海運": "039", "社会保険": "040",
    "司法": "041", "災害対策": "042", "農業": "043", "航空": "044", "防衛": "045",
    "民事": "046", "建築・住宅": "047", "林業": "048", "貨物運送": "049", "外事": "050"
}

# ==========================================
# 3. 関数定義
# ==========================================

@st.cache_data(ttl=3600)
def fetch_laws_by_category(category_name):
    """ジャンルごとの法令リスト取得"""
    if category_name == "すべて":
        try:
            response = requests.get(API_V1_LIST_URL, timeout=60)
            response.raise_for_status()
            root = ET.fromstring(response.content)
            law_list = []
            for info in root.iter("LawNameListInfo"):
                name = info.find("LawName").text if info.find("LawName") is not None else ""
                law_id = info.find("LawId").text if info.find("LawId") is not None else ""
                law_list.append({
                    "LawName": name,
                    "LawId": law_id,
                    "DisplayLabel": name
                })
            return pd.DataFrame(law_list)
        except Exception as e:
            st.error(f"全法令リストの取得に失敗しました: {e}")
            return pd.DataFrame()
    else:
        code = OFFICIAL_CATEGORY_MAP.get(category_name)
        if not code: return pd.DataFrame()
        try:
            params = {"category_cd": code, "limit": 1000}
            response = requests.get(API_V2_LIST_URL, params=params, timeout=60)
            response.raise_for_status()
            data = response.json()
            laws_data = data.get("laws", [])
            law_list = []
            for item in laws_data:
                info = item.get("current_revision_info", {})
                if not info: continue
                name = info.get("law_title", "")
                kana = info.get("law_title_kana", "")
                abbrev = info.get("abbrev", "")
                law_id = item.get("law_info", {}).get("law_id") or info.get("law_revision_id", "").split("_")[0]
                display_label = name
                if abbrev: display_label += f" 【略: {abbrev}】"
                law_list.append({
                    "LawName": name,
                    "LawNameKana": kana,
                    "LawId": law_id,
                    "DisplayLabel": display_label
                })
            df = pd.DataFrame(law_list)
            if not df.empty and "LawNameKana" in df.columns:
                df = df.sort_values(by="LawNameKana")
            return df
        except Exception as e:
            st.error(f"リスト取得エラー: {e}")
            return pd.DataFrame()

def fetch_law_xml_bytes(law_id):
    """詳細XML取得"""
    url = f"{API_V1_DETAILS_URL}/{law_id}"
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.content
    except: return None

def process_images_from_bytes(xml_bytes):
    """画像抽出"""
    image_files = {}
    try:
        root = ET.fromstring(xml_bytes)
        for elem in root.iter():
            if "ImageData" in elem.tag and elem.text:
                try:
                    zip_bytes = base64.b64decode(elem.text)
                    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
                        for filename in z.namelist():
                            image_files[filename] = z.read(filename)
                except: continue
    except: pass 
    return image_files

def convert_law_to_markdown_v2(xml_bytes):
    """Markdown変換（別表の表組み対応版）"""
    try: root = ET.fromstring(xml_bytes)
    except: return "XML Parse Error"

    law_title = root.find(".//LawTitle").text if root.find(".//LawTitle") is not None else ""
    law_num = root.find(".//LawNum").text if root.find(".//LawNum") is not None else ""
    md_text = f"# {law_title}\n{law_num}\n\n"

    # 条文
    articles = root.findall(".//Article")
    if not articles:
        main_prov = root.find(".//MainProvision")
        if main_prov:
            for p in main_prov.findall("./Paragraph"):
                p_num = p.find("ParagraphNum").text or ""
                p_sent = "".join(p.find(".//Sentence").itertext()) if p.find(".//Sentence") is not None else ""
                md_text += f"### {p_num}\n{p_sent}\n\n"

    for article in articles:
        caption = article.find("ArticleCaption").text or "" if article.find("ArticleCaption") is not None else ""
        title = article.find("ArticleTitle").text or "" if article.find("ArticleTitle") is not None else ""
        md_text += f"## {caption} {title}\n"
        for p in article.findall("Paragraph"):
            p_num = p.find("ParagraphNum").text or "" if p.find("ParagraphNum") is not None else ""
            p_sent = "".join(p.find(".//Sentence").itertext()) if p.find(".//Sentence") is not None else ""
            md_text += f"### {p_num}\n{p_sent}\n\n"
            for item in p.findall("Item"):
                i_title = item.find("ItemTitle").text or "・" if item.find("ItemTitle") is not None else "・"
                i_sent = "".join(item.find(".//Sentence").itertext()) if item.find(".//Sentence") is not None else ""
                md_text += f"- **{i_title}** {i_sent}\n"
                for sub in item.findall("Subitem1"):
                    s_title = sub.find("Subitem1Title").text or "" if sub.find("Subitem1Title") is not None else ""
                    s_sent = "".join(sub.find(".//Sentence").itertext()) if sub.find(".//Sentence") is not None else ""
                    md_text += f"    - **{s_title}** {s_sent}\n"

    # 別表 (AppdxTable)
    for tbl in root.findall(".//AppdxTable"):
        # タイトル取得
        title_elem = tbl.find("AppdxTableTitle")
        title = title_elem.text.strip() if (title_elem is not None and title_elem.text) else "別表"
        md_text += f"\n## {title}\n\n"

        # Tableタグがあるか確認
        table_elem = tbl.find(".//Table")
        
        # Tableがない場合（テキストのみの場合など）は従来通りテキストとして出力
        if table_elem is None:
            content = "".join(tbl.itertext())
            content = re.sub(r'\s+', ' ', content).strip()
            md_text += f"> {content[:1000]}...\n\n"
            continue

        # TableRowを取得
        rows = table_elem.findall(".//TableRow")
        if not rows:
            continue
        
        markdown_rows = []
        
        # 各行を処理
        for row in rows:
            cols = []
            for col in row.findall(".//TableColumn"):
                # セル内のテキストを取得して整形
                text = "".join(col.itertext())
                text = re.sub(r'\s+', ' ', text).strip()
                # 読みやすくするために「。」の後に改行タグを入れる
                text = text.replace("。", "。<br>")
                cols.append(text)
            markdown_rows.append(cols)

        # 列数を統一（Markdownの表崩れ防止）
        if not markdown_rows:
            continue
            
        max_cols = max(len(r) for r in markdown_rows)
        if max_cols == 0:
            continue

        for r in markdown_rows:
            while len(r) < max_cols:
                r.append("")

        # Markdownテーブルの生成
        # 1行目をヘッダーとして扱う
        header_row = markdown_rows[0]
        md_text += "| " + " | ".join(header_row) + " |\n"
        # 区切り線
        md_text += "| " + " | ".join(["---"] * max_cols) + " |\n"
        # データ行（2行目以降）
        for row in markdown_rows[1:]:
             md_text += "| " + " | ".join(row) + " |\n"
        
        md_text += "\n"

    return md_text

# ==========================================
# 4. メイン処理 (View)
# ==========================================

def main():
    # バナー画像の表示
    try:
        st.image("images/banner.png", use_container_width=True)
    except:
        st.warning("⚠️ 画像が見つかりません。imagesフォルダに 'banner.png' があるか確認してください")

    st.markdown("### 🐶 法令、とってきました。")
    st.caption("AIのための法令あつめ、わたしが代わりにやっておきます。")

    # ==========================================
    # ★ 使い方ガイド＆AI活用レシピ
    # ==========================================
    with st.expander("🔰 使い方＆AI活用レシピ（ボクにお任せください！）"):
        st.markdown("##### 🐶 「ご主人様、AIに読ませる法令集めはボクがやります！」")
        st.caption("面倒なコピー＆ペーストは不要です。ボクが「AIが一番読みやすい形」に整えてお届けします。")
        
        st.markdown("---")
        step1, step2, step3 = st.columns(3)
        with step1:
            st.info("**Step 1. 探す** クンクン")
            st.markdown("###### 🏛️ ジャンルを選ぶ")
            st.caption("「建築」や「労働」など、気になる分野を選んでください。「すべて」なら全法令から探し出します！")
        with step2:
            st.info("**Step 2. 集める** パクッ")
            st.markdown("###### 🛒 リストに追加")
            st.caption("法令名を入力して、必要なものをカートに入れてください。間違えたら「削除」でペッと吐き出せます。")
        with step3:
            st.info("**Step 3. お届け** タッタッ")
            st.markdown("###### 📦 まとめてDL")
            st.caption("オレンジのボタンを押せば、すべての法令を整理整頓して、ZIPファイルでお届けします！")

        st.markdown("---")
        st.markdown("##### 💡 ダウンロードしたデータの活用レシピ")
        st.caption("お届けしたファイル（Markdown形式）は、ChatGPTやNotebookLMの大好物です。")

        st.markdown("**1️⃣ NotebookLM で「法令マスター」を作る**")
        st.code("【手順】\n1. ダウンロードしたZIPファイルを一度「解凍」する\n2. フォルダの中にある「.mdファイル」をNotebookLMにアップロード！\n\n【聞いてみよう】\n「新人研修のために、この法律の重要なポイントをスライド構成にまとめて」\n「第〇条の要件を、箇条書きで分かりやすく整理して」", language="text")

        st.markdown("**2️⃣ ChatGPT で「条文チェックリスト」を作る**")
        st.code("【手順】必要な法律のファイル(.md)をアップロードして指示する。\n\n【聞いてみよう】\n「建設業法_2026xxxx.md を読み込んで、請負業者の責務に関するチェックリストを表形式で作って」", language="text")

        st.error("⚠️ **【重要】AIのご利用に関するご注意**\n\nAIはもっともらしい嘘（ハルシネーション）をつくことがあります。特に法令の解釈や適法性の判断については、AIの回答を鵜呑みにせず、必ず**「法令の原文」**や**「公式のガイドライン」**をご自身で確認してください。")

    # セッション状態の初期化
    if "selected_cart" not in st.session_state:
        st.session_state["selected_cart"] = []

    # --- Step 1: ジャンル (公式分類) ---
    st.markdown("### Step 1. ジャンルを選んでください")
    genre_options = ["すべて"] + list(OFFICIAL_CATEGORY_MAP.keys())
    selected_genre = st.selectbox("ジャンルを選択", options=genre_options)

    # --- データ取得 ---
    with st.spinner(f"「{selected_genre}」の法令を探しています...🐶"):
        df_laws = fetch_laws_by_category(selected_genre)

    if df_laws.empty:
        st.warning("法令リストが取得できませんでした。")
        return

    # --- Step 2: 検索＆追加 ---
    st.markdown(f"### Step 2. 法令を探してリストに追加")
    st.caption(f"🔍 現在、**{len(df_laws):,}** 件から検索できます")

    # --- ★追加機能：プリセット法令読み込み ---
    with st.expander("📚 おすすめセットを一括追加"):
        st.info("よく使われる法令をまとめてリストに追加します。")
        if st.button("🏗️ 建築基準法関係規定セット（建築基準法、都市計画法、消防法など約70件）"):
            with st.spinner("全法令データベースから対象の法令を探しています...（少し時間がかかります）"):
                # プリセットはジャンルをまたぐため、全法令リストから検索する
                all_laws_df = fetch_laws_by_category("すべて")
                
                added_count = 0
                if not all_laws_df.empty:
                    for target_name in PRESET_CONSTRUCTION_LAWS:
                        # 法令名で完全一致検索
                        match = all_laws_df[all_laws_df["LawName"] == target_name]
                        if not match.empty:
                            display_label = match.iloc[0]["DisplayLabel"]
                            # まだカートになければ追加
                            if display_label not in st.session_state["selected_cart"]:
                                st.session_state["selected_cart"].append(display_label)
                                added_count += 1
                
                if added_count > 0:
                    st.success(f"{added_count}件の法令を追加しました！")
                    st.rerun()
                else:
                    st.warning("追加できる法令が見つかりませんでした（既に追加済みか、データが見つかりません）。")


    options = df_laws["DisplayLabel"].tolist()
    
    # 追加処理（コールバック）
    def add_to_cart():
        new_items = st.session_state.temp_search_box
        for item in new_items:
            if item not in st.session_state["selected_cart"]:
                st.session_state["selected_cart"].append(item)
        st.session_state.temp_search_box = []

    # 検索ボックス
    st.multiselect(
        "法令名・略称で検索（選ぶと下のリストに移動します）",
        options=options,
        placeholder="キーワードを入力...（例：建築基準法）",
        key="temp_search_box",
        on_change=add_to_cart
    )
    
    # ----------------------------------------------
    # 選んだ法令リストの表示エリア
    # ----------------------------------------------
    st.markdown("#### 📄 選んだ法令リスト（ここに溜まります）")
    
    if not st.session_state["selected_cart"]:
        st.info("まだ何も選ばれていません。上の検索ボックスから追加してください。")
    else:
        with st.container(border=True):
            items_to_remove = []
            for item in st.session_state["selected_cart"]:
                c1, c2 = st.columns([0.85, 0.15])
                with c1:
                    st.write(f"・ {item}")
                with c2:
                    if st.button("削除", key=f"del_{item}"):
                        items_to_remove.append(item)
            
            if items_to_remove:
                for rm_item in items_to_remove:
                    st.session_state["selected_cart"].remove(rm_item)
                st.rerun()

    # --- Step 3: 便利機能 ---
    st.markdown("")
    with st.expander("📂 その他の便利機能（リスト保存・読込）"):
        current_selection = st.session_state["selected_cart"]
        if current_selection:
            json_str = json.dumps(current_selection, ensure_ascii=False, indent=2)
            st.download_button("今のリストを保存する (JSON)", json_str, "my_law_set.json", "application/json")
        
        uploaded_file = st.file_uploader("保存したリストを読み込む", type=["json"])
        if uploaded_file and st.button("このリストを適用する"):
            try:
                loaded_data = json.load(uploaded_file)
                st.session_state["selected_cart"] = loaded_data
                st.rerun()
            except:
                st.error("ファイルの読み込みに失敗しました。")

    # --- Step 4: ダウンロード ---
    st.markdown("### Step 3. ダウンロード")
    
    if st.session_state["selected_cart"]:
        count = len(st.session_state["selected_cart"])
        if st.button(f"🐶 {count}件の法令データをZIPでダウンロード"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            zip_buffer = io.BytesIO()
            
            today_str = datetime.now().strftime('%Y%m%d')
            
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                total = len(st.session_state["selected_cart"])
                
                # ダウンロード時は、各法令が属するジャンルに関わらず「全法令」から検索する必要がある場合がある
                # （プリセットで追加された法令が、現在の選択ジャンルに含まれていない可能性があるため）
                
                # 効率化のため、もし現在のdf_lawsで見つからなければ、all_lawsをfetchする
                all_laws_cache = None
                
                for i, display_label in enumerate(st.session_state["selected_cart"]):
                    # まず現在のジャンルリストから探す
                    rows = df_laws[df_laws["DisplayLabel"] == display_label]
                    
                    if rows.empty:
                        # 見つからない場合は全リストを取得して探す（初回のみロード）
                        if all_laws_cache is None:
                            status_text.text("他のジャンルの法令を探しています...")
                            all_laws_cache = fetch_laws_by_category("すべて")
                        
                        rows = all_laws_cache[all_laws_cache["DisplayLabel"] == display_label]

                    if not rows.empty:
                        law_name = rows.iloc[0]["LawName"]
                        law_id = rows.iloc[0]["LawId"]
                        
                        status_text.text(f"取得中: {law_name} ...")
                        xml_bytes = fetch_law_xml_bytes(law_id)
                        
                        if xml_bytes:
                            images = process_images_from_bytes(xml_bytes)
                            for img_name, img_data in images.items():
                                zf.writestr(f"images/{img_name}", img_data)
                            
                            md_content = convert_law_to_markdown_v2(xml_bytes)
                            
                            filename = f"{law_name}_{today_str}.md"
                            zf.writestr(filename, md_content)
                    else:
                        law_name = display_label.split(" 【")[0]
                        status_text.warning(f"「{law_name}」のデータが見つかりませんでした。スキップします。")

                    progress_bar.progress((i + 1) / total)
            
            status_text.text("完了しました！ワン！🐶")
            zip_buffer.seek(0)
            
            zip_filename = f"法令データセット_{today_str}.zip"
            
            st.download_button(
                label="📦 ZIPファイルを保存する",
                data=zip_buffer,
                file_name=zip_filename,
                mime="application/zip"
            )
    else:
        st.warning("☝️ まずは法令を選んでリストに追加してください")

    # ----------------------------------------------
    # フッター
    # ----------------------------------------------
    st.markdown("---")
    
    f_col1, f_col2 = st.columns([0.4, 0.6])
    
    with f_col1:
        st.caption("訪問者数：")
        st.markdown(
            """
            ![Visitor Count](https://visitor-badge.laobi.icu/badge?page_id=satoshin_law_totte_app_v1&right_color=orange&left_text=Visitors)
            """,
            unsafe_allow_html=True
        )
        
    with f_col2:
        st.markdown("##### 🦁 お問い合わせ・改善提案")
        st.caption(
            """
            アプリへのご意見や改善提案は、  
            **Discord** または **リベシティ** にて、  
            **『さとしん』** 宛にご連絡ください。
            """
        )
        # ボタンを2つ並べて表示
        st.link_button("💬 Discord でメッセージを送る", "https://discordapp.com/users/1178537787662815324")
        st.link_button("🦁 リベシティ「さとしん」プロフィール", "https://libecity.com/user_profile/Yn4UTV5ALtd8JY2y0WUSEofjYP33")

if __name__ == "__main__":
    main()