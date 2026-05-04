from flask import Flask, request, redirect, jsonify
import json
import os
import copy

app = Flask(__name__)

# 保存ファイルのパス
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data.json")

# 初期メニューデータ
default_data = {
    "menu": {
        "焼き鳥": [
            {"name": "皮（タレ）", "price": 120}, {"name": "皮（塩）", "price": 120},
            {"name": "レバー（タレ）", "price": 150}, {"name": "レバー（塩）", "price": 150},
            {"name": "四つ身モモ（タレ）", "price": 150}, {"name": "四つ身モモ（塩）", "price": 150},
            {"name": "砂ズリ", "price": 150}, {"name": "豚バラ", "price": 180},
            {"name": "ささみ（うめ）", "price": 200}, {"name": "ささみ（わさび）", "price": 200},
            {"name": "つくね（タレ）", "price": 150}, {"name": "つくね（塩）", "price": 150},
            {"name": "なんこつつくね", "price": 200}, {"name": "ウインナー", "price": 180},
            {"name": "ピリ辛ウインナー", "price": 180}, {"name": "チーズ巻", "price": 220},
            {"name": "うずら巻", "price": 220}, {"name": "梅しそ巻", "price": 220},
            {"name": "手羽先", "price": 200}, {"name": "丸腸", "price": 350},
            {"name": "サガリ", "price": 350}, {"name": "しいたけ", "price": 180},
            {"name": "ネギ", "price": 150}, {"name": "ピーマン", "price": 150}
        ],
        "刺身": [
            {"name": "鳥刺し", "price": 880}, {"name": "馬刺し", "price": 1680},
            {"name": "馬レバー刺し", "price": 1680}
        ],
        "一品料理": [
            {"name": "鶏からあげ", "price": 700}, {"name": "だし巻きたまご", "price": 600},
            {"name": "たこ唐揚げ", "price": 650}, {"name": "ゲソ唐揚げ", "price": 650},
            {"name": "ホルモン鉄板", "price": 900}, {"name": "ポテトフライ", "price": 550},
            {"name": "とり皮ぎょうざ", "price": 650}, {"name": "チーズフライ", "price": 450},
            {"name": "枝豆", "price": 350}, {"name": "冷奴", "price": 400},
            {"name": "板わさ", "price": 400}, {"name": "チャンジャ", "price": 400},
            {"name": "たこわさ", "price": 400}, {"name": "漬物盛り合わせ", "price": 400}
        ],
        "ご飯もの": [
            {"name": "お茶漬け（のり）", "price": 550}, {"name": "お茶漬け（梅）", "price": 550},
            {"name": "お茶漬け（しゃけ）", "price": 550}, {"name": "おにぎり", "price": 180},
            {"name": "焼おにぎり", "price": 250}, {"name": "白ごはん", "price": 300}
        ]
    },
    "people": {}
}

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return copy.deepcopy(default_data)
    return copy.deepcopy(default_data)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# スタイル
BASE_STYLE = """
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body { font-family: sans-serif; background:#1f1510; color:#fff; margin:0; padding:14px; font-size:18px; line-height:1.4; }
h2 { font-size:24px; border-bottom:2px solid #d79b3d; padding-bottom:5px; margin-bottom:15px; }
h3 { font-size:20px; color:#d79b3d; margin-top:20px; border-left: 4px solid #d79b3d; padding-left:10px; }
.card { background:#2c1c14; padding:14px; margin:10px 0; border-radius:12px; border:1px solid #3d2b21; }
.btn { display:inline-block; padding:14px 16px; border-radius:10px; text-decoration:none; font-size:18px; text-align:center; border:none; cursor:pointer; font-weight:bold; }
.btn-yellow { background:#d79b3d; color:#000; }
.btn-red { background:#dc3545; color:#fff; }
.btn-gray { background:#444; color:#fff; }
.btn-outline { background:transparent; border:1px solid #d79b3d; color:#d79b3d; }
input { width:100%; padding:12px; font-size:16px; border-radius:8px; border:none; box-sizing:border-box; background:#3d2b21; color:#fff; }
.small-btn { width:44px; height:44px; font-size:24px; border-radius:8px; border:none; background:#d79b3d; color:#000; font-weight:bold; display:flex; align-items:center; justify-content:center; }
.qty-display { font-size:24px; font-weight:bold; margin:0 15px; min-width:35px; text-align:center; color:#d79b3d; }
.footer-controls { position: fixed; bottom: 0; left: 0; width: 100%; background: rgba(31, 21, 16, 0.95); padding: 15px; box-sizing: border-box; border-top: 1px solid #3d2b21; z-index: 1000; display: flex; gap: 10px; }
.footer-spacer { height: 120px; }
</style>
"""

@app.route("/")
def index():
    data = load_data()
    people_html = "".join([f'<a class="btn btn-yellow" href="/order?person={p}" style="margin:5px;">{p}{" (確定)" if data["people"][p].get("confirmed") else ""}</a>' for p in data["people"]])
    return f"""
    <html><head>{BASE_STYLE}</head><body>
    <h2>🍢 家族の焼き鳥注文</h2>
    <form action="/enter"><input name="person" placeholder="名前を入力（例：お父さん）" required><button class="btn btn-yellow" style="width:100%; margin-top:5px;">入室</button></form>
    <h3>参加メンバー</h3>
    <div style="display:flex; flex-wrap:wrap;">{people_html if people_html else '<div style="opacity:0.6;">参加者がいません</div>'}</div>
    <hr style="margin:30px 0; border:0; border-top:1px solid #444;">
    <a class="btn btn-outline" href="/summary" style="width:100%; box-sizing:border-box;">📊 集計画面</a>
    <br><br><a class="btn btn-gray" href="/menu_admin" style="width:100%; box-sizing:border-box; font-size:14px; opacity:0.6;">⚙️ メニュー編集</a>
    </body></html>
    """

@app.route("/enter")
def enter():
    person = request.args.get("person", "").strip()
    if not person: return redirect("/")
    return redirect(f"/order?person={person}")

@app.route("/order")
def order():
    data = load_data()
    person = request.args.get("person")
    if not person: return redirect("/")
    if person not in data["people"]:
        data["people"][person] = {"order": {}, "confirmed": False}
        save_data(data)
    info = data["people"][person]
    order, confirmed = info["order"], info.get("confirmed", False)
    price_map = {i["name"]: i["price"] for cat in data["menu"].values() for i in cat}
    my_subtotal = sum(price_map.get(name, 0) * qty for name, qty in order.items())

    html = f"<html><head>{BASE_STYLE}</head><body>"
    html += f"<div style='position:sticky; top:0; z-index:900; background:#d79b3d; color:#000; padding:10px; border-radius:0 0 8px 8px; font-weight:bold; text-align:center;'>{person} 様の小計: ¥{my_subtotal}</div>"
    
    for cat, items in data["menu"].items():
        html += f"<h3>{cat}</h3>"
        for i in items:
            qty = order.get(i["name"], 0)
            html += f"""<div class="card"><div style="display:flex; justify-content:space-between; align-items:center;"><div><b>{i['name']}</b><br><small>¥{i['price']}</small></div><div style="display:flex; align-items:center;"><button class="small-btn" onclick="upd('{person}','{i['name']}','remove')" {'disabled' if confirmed else ''}>−</button><span class="qty-display">{qty}</span><button class="small-btn" onclick="upd('{person}','{i['name']}','add')" {'disabled' if confirmed else ''}>＋</button></div></div></div>"""

    html += f"""
    <div class="footer-spacer"></div>
    <div class="footer-controls">
        <a class="btn btn-gray" href="/" style="flex: 1;">戻る</a>
        <a class="btn {'btn-red' if confirmed else 'btn-yellow'}" href="/toggle_confirm?person={person}" style="flex: 2;">
            {'⚠️ 確定解除' if confirmed else '🚀 注文を確定'}
        </a>
    </div>
    <script>function upd(p, i, a){{ fetch(`/${{a}}?person=${{encodeURIComponent(p)}}&item=${{encodeURIComponent(i)}}`).then(()=>location.reload()); }}</script>
    </body></html>
    """
    return html

@app.route("/summary")
def summary():
    data = load_data()
    price_map = {i["name"]: i["price"] for cat in data["menu"].values() for i in cat}
    total_items, grand_total, people_cards = {}, 0, ""
    for person, info in data["people"].items():
        subtotal, lines = 0, ""
        for item, qty in info["order"].items():
            if qty > 0:
                p = price_map.get(item, 0)
                lines += f"<div style='display:flex; justify-content:space-between;'><span>{item} × {qty}</span><span>¥{p*qty}</span></div>"
                total_items[item] = total_items.get(item, 0) + qty
                subtotal += p * qty
        if subtotal > 0:
            people_cards += f'<div class="card"><div style="display:flex; justify-content:space-between; border-bottom:1px solid #444; margin-bottom:8px;"><strong>{person}</strong><a href="/delete_person?person={person}" style="color:#888; font-size:12px;">削除</a></div>{lines}<div style="text-align:right; color:#d79b3d; font-weight:bold;">小計 ¥{subtotal}</div></div>'
            grand_total += subtotal
    total_list = "".join([f"<div style='font-size:20px; border-bottom:1px solid #3d2b21; padding:8px 0;'><b style='color:#d79b3d; font-size:24px;'>{v}</b> × {k}</div>" for k,v in total_items.items()])
    return f"<html><head>{BASE_STYLE}</head><body><h2>📊 集計結果</h2><div class='card'>{total_list if total_list else '注文なし'}<div style='text-align:right; font-size:28px; font-weight:bold; color:#d79b3d; margin-top:15px;'>総計 ¥{grand_total}</div></div><h3>内訳</h3>{people_cards}<br><a class='btn btn-gray' href='/' style='width:100%; box-sizing:border-box;'>戻る</a></body></html>"

@app.route("/menu_admin")
def menu_admin():
    data = load_data()
    menu_html = ""
    for cat, items in data["menu"].items():
        menu_html += f"<h3>{cat}</h3>"
        for i in items:
            menu_html += f"""
            <div class="card" style="padding:10px;">
                <form action="/update_menu_item" style="display:flex; align-items:center; gap:5px; margin:0;">
                    <span style="flex:2; font-size:14px;">{i['name']}</span>
                    <input type="hidden" name="cat" value="{cat}">
                    <input type="hidden" name="old_name" value="{i['name']}">
                    <input type="number" name="price" value="{i['price']}" style="flex:1; width:60px;">
                    <button class="btn btn-yellow" style="padding:5px 10px; font-size:12px;">更</button>
                    <a href="/del_menu_item?cat={cat}&name={i['name']}" class="btn btn-red" style="padding:5px 10px; font-size:12px;">消</a>
                </form>
            </div>"""
    return f"""
    <html><head>{BASE_STYLE}</head><body>
    <h2>⚙️ メニュー編集</h2>
    <div class="card">
        <b>新メニュー追加</b>
        <form action="/update_menu_item">
            <input name="cat" placeholder="カテゴリ" required>
            <input name="new_name" placeholder="品名" required>
            <input name="price" type="number" placeholder="価格" required>
            <button class="btn btn-yellow" style="width:100%; margin-top:5px;">追加</button>
        </form>
    </div>
    {menu_html}
    <br><a class="btn btn-gray" href="/" style="width:100%; box-sizing:border-box;">戻る</a>
    </body></html>
    """

@app.route("/update_menu_item")
def update_menu_item():
    data = load_data()
    cat, old_name, new_name = request.args.get("cat"), request.args.get("old_name"), request.args.get("new_name")
    price = int(request.args.get("price", 0))
    if cat not in data["menu"]: data["menu"][cat] = []
    if old_name:
        for i in data["menu"][cat]:
            if i["name"] == old_name: i["price"] = price
    elif new_name:
        data["menu"][cat].append({"name": new_name, "price": price})
    save_data(data)
    return redirect("/menu_admin")

@app.route("/del_menu_item")
def del_menu_item():
    data = load_data()
    cat, name = request.args.get("cat"), request.args.get("name")
    if cat in data["menu"]:
        data["menu"][cat] = [i for i in data["menu"][cat] if i["name"] != name]
        save_data(data)
    return redirect("/menu_admin")

@app.route("/add")
def add():
    data = load_data()
    p, i = request.args.get("person"), request.args.get("item")
    if p and i and not data["people"][p].get("confirmed"):
        data["people"][p]["order"][i] = data["people"][p]["order"].get(i, 0) + 1
        save_data(data)
    return jsonify({"ok": True})

@app.route("/remove")
def remove():
    data = load_data()
    p, i = request.args.get("person"), request.args.get("item")
    if p and i and not data["people"][p].get("confirmed"):
        order = data["people"][p]["order"]
        if i in order:
            if order[i] <= 1: del order[i]
            else: order[i] -= 1
            save_data(data)
    return jsonify({"ok": True})

@app.route("/toggle_confirm")
def toggle_confirm():
    data = load_data()
    p = request.args.get("person")
    if p in data["people"]:
        # 状態を反転
        is_confirmed = not data["people"][p].get("confirmed", False)
        data["people"][p]["confirmed"] = is_confirmed
        save_data(data)
        
        # 確定した場合は集計画面へ、解除した場合は注文画面に戻る
        if is_confirmed:
            return redirect("/summary")
        else:
            return redirect(f"/order?person={p}")
    return redirect("/")

@app.route("/delete_person")
def delete_person():
    data = load_data()
    p = request.args.get("person")
    if p in data["people"]:
        del data["people"][p]
        save_data(data)
    return redirect("/summary")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
