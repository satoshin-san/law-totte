# test_v2.py
import requests
import json

def check_v2_abbreviations():
    print("🔍 API v2 から法令リスト（JSON）を取得して、略称をチェックします...")
    
    # API v2 の法令一覧取得エンドポイント
    url = "https://laws.e-gov.go.jp/api/2/laws"
    
    try:
        # JSONで取得
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # データの中身を確認（法令リストは 'laws' キーに入っていると想定）
        # ※実際のキー名はAPI仕様によりますが、一般的な構造として探索します
        laws = data.get("laws", [])
        if not laws:
            # 構造が違う場合、ルートそのものがリストか確認
            if isinstance(data, list):
                laws = data
            else:
                # 念のためデータ構造の一部を表示
                print("⚠️ データ構造が予想と違いました。最初の要素を表示します:")
                print(str(data)[:500])
                return

        print(f"✅ 取得成功！ 全 {len(laws)} 件の法令が見つかりました。\n")
        
        print("--- 略称（abbreviation）が登録されている法令の例 ---")
        count = 0
        for law in laws:
            # 略称フィールドがあるか確認（キー名は推測：abbreviation, Ryakusho など）
            # 実際のレスポンスを見て調整する必要がありますが、まずは 'LawName' と対になるものを探します
            name = law.get("LawName") or law.get("name")
            abbrev = law.get("Abbreviation") or law.get("abbreviation")
            
            if abbrev:
                print(f"📄 {name} \t→ 略称: {abbrev}")
                count += 1
                if count >= 20:  # 20件見つかったら終了
                    break
        
        if count == 0:
            print("😢 この20件の中に略称データは見つかりませんでした（またはキー名が違います）。")
            # データのサンプルを表示してキー名を確認
            print("\n🔍 データのサンプル（1件目）:")
            print(json.dumps(laws[0], ensure_ascii=False, indent=2))

    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")

if __name__ == "__main__":
    check_v2_abbreviations()