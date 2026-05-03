from flask import Flask, request, redirect, jsonify
import json
import os
import copy

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data.json")

# =========================
# 初期データ
# =========================
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
            {"name": "鳥刺し", "price": 880},
            {"name": "馬刺し", "price": 1680},
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
            {"name": "お茶漬け（のり）", "price": 550},
            {"name": "お茶漬け（梅）", "price": 550},
            {"name": "お茶漬け（しゃけ）", "price": 550},
            {"name": "おにぎり", "price": 180},
            {"name": "焼おにぎり", "price": 250},
            {"name": "白ごはん", "price": 300}
        ]
    },
    "people": {}
}

# =========================
# データ処理
# =========================
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

# =========================
# UI
# =========================
BASE_STYLE = """
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body { font-family:sans-serif; background:#1f1510; color:#fff; margin:0; padding:14px; font-size:18px; }
h2 { border-bottom:2px solid #d79b3d; padding-bottom:5px; }
h3 { color:#d79b3d; margin-top:20px; }
.card { background:#2c1c14; padding:14px; margin:10px 0; border-radius:12px; }
.btn { padding:12px 16px; border-radius:10px; display:inline-block; text-decoration:none; text-align:center; }
.btn-yellow { background:#d79b3d; color:#000; font-weight:bold; }
.btn-gray { background:#444; color:#fff; }
.small-btn { padding:8px 14px; background:#d79b3d; border:none; border-radius:8px; font-size:18px; }
.qty { margin:0 12px; font-weight:bold; font-size:20px; }
</style>
"""

# =========================
# トップ
# =========================
@app.route("/")
def index():
    data = load_data()
    people = ""

    for p in data["people"]:
        mark = " ✔" if data["people"][p].get("confirmed") else ""
        people += f'<a class="btn btn-yellow" href="/order?person={p}">{p}{mark}</a> '

    return f"""
    <html><head>{BASE_STYLE}</head><body>
    <h2>🍢 家族注文</h2>

    <form action="/enter">
        <input name="person" placeholder="名前">
        <button class="btn btn-yellow" style="width:100%;">入室</button>
    </form>

    <h3>メンバー</h3>
    {people if people else "なし"}

    <br><br>
    <a class="btn btn-gray" href="/summary">集計</a>
    </body></html>
    """

@app.route("/enter")
def enter():
    return redirect(f"/order?person={request.args.get('person')}")

# =========================
# 注文
# =========================
@app.route("/order")
def order():
    data = load_data()
    person = request.args.get("person")
    if not person:
        return redirect("/")

    if person not in data["people"]:
        data["people"][person] = {"order": {}, "confirmed": False}
        save_data(data)

    info = data["people"][person]
    order = info["order"]
    confirmed = info["confirmed"]

    html = f"<html><head>{BASE_STYLE}</head><body>"
    html += f"<h2>{person}</h2>"

    if confirmed:
        html += "<div class='card'>✔ 確定済み</div>"

    for cat, items in data["menu"].items():
        html += f"<h3>{cat}</h3>"
        for i in items:
            qty = order.get(i["name"], 0)

            html += f"""
            <div class="card">
                <div style="display:flex; justify-content:space-between;">
                    <div>{i['name']}<br>¥{i['price']}</div>
                    <div>
                        <button class="small-btn" onclick="upd('{person}','{i['name']}','remove')" {'disabled' if confirmed else ''}>−</button>
                        <span class="qty">{qty}</span>
                        <button class="small-btn" onclick="upd('{person}','{i['name']}','add')" {'disabled' if confirmed else ''}>＋</button>
                    </div>
                </div>
            </div>
            """

    html += f"""
    <a class="btn btn-yellow" href="/toggle_confirm?person={person}" style="width:100%;">
        {'解除' if confirmed else '確定'}
    </a>

    <script>
    function upd(p,i,a){{
        fetch(`/${{a}}?person=${{p}}&item=${{i}}`)
        .then(()=>location.reload());
    }}
    </script>
    </body></html>
    """
    return html

# =========================
# 追加・削除
# =========================
@app.route("/add")
def add():
    data = load_data()
    p, i = request.args.get("person"), request.args.get("item")

    if p and i and not data["people"][p]["confirmed"]:
        o = data["people"][p]["order"]
        o[i] = o.get(i, 0) + 1
        save_data(data)

    return jsonify({"ok": True})


@app.route("/remove")
def remove():
    data = load_data()
    p, i = request.args.get("person"), request.args.get("item")

    if p and i and not data["people"][p]["confirmed"]:
        o = data["people"][p]["order"]
        if i in o:
            if o[i] <= 1:
                del o[i]
            else:
                o[i] -= 1
            save_data(data)

    return jsonify({"ok": True})

# =========================
# 確定
# =========================
@app.route("/toggle_confirm")
def toggle_confirm():
    data = load_data()
    p = request.args.get("person")
    if p in data["people"]:
        data["people"][p]["confirmed"] = not data["people"][p]["confirmed"]
        save_data(data)
    return redirect(f"/order?person={p}")

# =========================
# 集計
# =========================
@app.route("/summary")
def summary():
    data = load_data()
    price = {i["name"]: i["price"] for c in data["menu"].values() for i in c}

    total = 0
    html = ""

    for p, info in data["people"].items():
        sub = 0
        lines = ""

        for i, q in info["order"].items():
            if q > 0:
                v = price.get(i, 0)
                lines += f"<div>{i} × {q} = ¥{v*q}</div>"
                sub += v * q

        total += sub

        html += f"<div class='card'><b>{p}</b>{lines}<hr>小計 ¥{sub}</div>"

    return f"""
    <html><head>{BASE_STYLE}</head><body>
    <h2>📊 集計</h2>
    {html}
    <h3>総計 ¥{total}</h3>
    <a class="btn btn-gray" href="/">戻る</a>
    </body></html>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
