from flask import Flask, request, redirect, jsonify
import json
import os
import copy

app = Flask(__name__)

DATA_FILE = "data.json"

default_data = {
    "menu": {
        "定番串": [
            {"name": "もも", "price": 150},
            {"name": "ねぎま", "price": 170}
        ],
        "人気串": [
            {"name": "つくね", "price": 180},
            {"name": "かわ", "price": 160}
        ]
    },
    "people": {}
}


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return copy.deepcopy(default_data)


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# =========================
# 共通CSS
# =========================
BASE_STYLE = """
<meta name="viewport" content="width=device-width, initial-scale=1">

<style>
body {
    font-family: sans-serif;
    background:#1f1510;
    color:#fff;
    margin:0;
    padding:14px;
    font-size:18px;
}

h2 { font-size:24px; }
h3 { font-size:20px; }

.card {
    background:#2c1c14;
    padding:14px;
    margin:10px 0;
    border-radius:12px;
}

.btn {
    display:inline-block;
    padding:12px 16px;
    border-radius:10px;
    text-decoration:none;
    font-size:18px;
}

.btn-yellow { background:#d79b3d; color:#000; }
.btn-gray { background:#444; color:#fff; }

input {
    width:100%;
    padding:12px;
    font-size:18px;
    margin:6px 0;
    border-radius:8px;
    border:none;
}

.small-btn {
    padding:10px 14px;
    font-size:18px;
}
</style>
"""


# =========================
# トップ
# =========================
@app.route("/")
def index():
    data = load_data()

    people_html = ""
    for p in data["people"]:
        people_html += f"""
        <a class="btn btn-yellow" href="/order?person={p}">
            {p}
        </a>
        """

    return f"""
    <html><head>{BASE_STYLE}</head>
    <body>

    <h2>🍢 焼き鳥注文</h2>

    <form action="/enter">
        <input name="person" placeholder="名前入力">
        <button class="btn btn-yellow">入室</button>
    </form>

    <h3>参加者</h3>
    <div>{people_html}</div>

    <hr>

    <a class="btn btn-yellow" href="/menu_admin">🍢 メニュー管理</a>
    <a class="btn btn-gray" href="/summary">📊 集計</a>

    </body></html>
    """


@app.route("/enter")
def enter():
    person = request.args.get("person")
    return redirect(f"/order?person={person}")


# =========================
# 注文
# =========================
@app.route("/order")
def order():
    data = load_data()
    person = request.args.get("person")

    if person not in data["people"]:
        data["people"][person] = {"order": {}}
        save_data(data)

    order = data["people"][person]["order"]

    html = f"""
    <html><head>{BASE_STYLE}</head>
    <body>

    <h2>👤 {person}</h2>
    """

    for cat, items in data["menu"].items():
        html += f"<h3>🍢 {cat}</h3>"

        for i in items:
            qty = order.get(i["name"], 0)

            html += f"""
            <div class="card">
                <div style="display:flex;justify-content:space-between;">
                    <div>
                        <div style="font-size:20px;">{i['name']}</div>
                        <div style="opacity:0.8;">¥{i['price']}</div>
                    </div>

                    <div>
                        <button class="small-btn"
                            onclick="updateQty('{person}','{i['name']}','add')">＋</button>

                        <span style="margin:0 10px;">{qty}</span>

                        <button class="small-btn"
                            onclick="updateQty('{person}','{i['name']}','remove')">−</button>
                    </div>
                </div>
            </div>
            """

    html += f"""
    <a class="btn btn-yellow" href="/confirm?person={person}">注文確定</a>

    <br><br>
    <a href="/">←戻る</a>

    <script>
    function updateQty(person,item,action){{
        fetch(`/${{action}}?person=${{person}}&item=${{item}}`)
            .then(()=>location.reload());
    }}
    </script>

    </body></html>
    """

    return html


@app.route("/add")
def add():
    data = load_data()
    person = request.args.get("person")
    item = request.args.get("item")

    data["people"][person]["order"][item] = data["people"][person]["order"].get(item, 0) + 1
    save_data(data)
    return jsonify({"ok": True})


@app.route("/remove")
def remove():
    data = load_data()
    person = request.args.get("person")
    item = request.args.get("item")

    if item in data["people"][person]["order"]:
        data["people"][person]["order"][item] = max(0, data["people"][person]["order"][item] - 1)

    save_data(data)
    return jsonify({"ok": True})


@app.route("/confirm")
def confirm():
    data = load_data()
    person = request.args.get("person")

    data["people"][person]["confirmed"] = True
    save_data(data)

    return redirect("/summary")


# =========================
# メニュー管理
# =========================
@app.route("/menu_admin")
def menu_admin():
    data = load_data()

    html = f"""
    <html><head>{BASE_STYLE}</head>
    <body>

    <h2>🍢 メニュー管理</h2>

    <div class="card">
        <input id="cat" placeholder="カテゴリ">
        <input id="name" placeholder="品名">
        <input id="price" placeholder="値段">

        <button class="btn btn-yellow" onclick="addMenu()">追加</button>
    </div>
    """

    for cat, items in data["menu"].items():
        html += f"<div class='card'><h3>{cat}</h3>"

        for i in items:
            html += f"""
            <div style="display:flex;justify-content:space-between;margin:8px 0;">
                <div>{i['name']} ¥{i['price']}</div>
                <a href="#" style="color:red;"
                   onclick="deleteMenu('{cat}','{i['name']}')">削除</a>
            </div>
            """

        html += "</div>"

    html += """
    <br>
    <a href="/">←戻る</a>

    <script>
    function addMenu(){
        const cat = document.getElementById("cat").value;
        const name = document.getElementById("name").value;
        const price = document.getElementById("price").value;

        fetch(`/add_menu?cat=${cat}&name=${name}&price=${price}`)
            .then(()=>location.reload());
    }

    function deleteMenu(cat,name){
        fetch(`/delete_menu?cat=${cat}&name=${name}`)
            .then(()=>location.reload());
    }
    </script>

    </body></html>
    """

    return html


@app.route("/add_menu")
def add_menu():
    data = load_data()

    cat = request.args.get("cat")
    name = request.args.get("name")
    price = request.args.get("price")

    data["menu"].setdefault(cat, []).append({
        "name": name,
        "price": int(price)
    })

    save_data(data)
    return jsonify({"ok": True})


@app.route("/delete_menu")
def delete_menu():
    data = load_data()

    cat = request.args.get("cat")
    name = request.args.get("name")

    data["menu"][cat] = [
        i for i in data["menu"][cat] if i["name"] != name
    ]

    if len(data["menu"][cat]) == 0:
        del data["menu"][cat]

    save_data(data)
    return jsonify({"ok": True})


# =========================
# 集計
# =========================
@app.route("/summary")
def summary():
    data = load_data()

    total = {}
    total_price = 0

    html = f"""
    <html><head>{BASE_STYLE}</head>
    <body>

    <h2>📊 集計</h2>

    <div class="card">
    <h3>全体</h3>
    """

    for person, info in data["people"].items():
        for item_name, qty in info["order"].items():

            price = 0
            for cat, items in data["menu"].items():
                for i in items:
                    if i["name"] == item_name:
                        price = i["price"]

            total[item_name] = total.get(item_name, 0) + qty
            total_price += price * qty

    for item, qty in total.items():
        html += f"<div>{item}: {qty}</div>"

    html += f"""
    <hr>
    <h3>💰 合計 ¥{total_price}</h3>
    </div>

    <h3>👤 人別内訳</h3>
    """

    for person, info in data["people"].items():

        person_total = 0

        html += f"<div class='card'><h3>{person}</h3>"

        for item_name, qty in info["order"].items():

            price = 0
            for cat, items in data["menu"].items():
                for i in items:
                    if i["name"] == item_name:
                        price = i["price"]

            person_total += price * qty

            html += f"<div>{item_name}: {qty}（¥{price * qty}）</div>"

        html += f"""
        <b>小計 ¥{person_total}</b><br>
        <a style="color:red;" href="/delete_person?person={person}">削除</a>
        </div>
        """

    html += """
    <br>
    <a href="/">←戻る</a>
    </body></html>
    """

    return html


@app.route("/delete_person")
def delete_person():
    data = load_data()
    person = request.args.get("person")

    if person in data["people"]:
        del data["people"][person]

    save_data(data)
    return redirect("/summary")


# =========================
# Render対応起動
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)