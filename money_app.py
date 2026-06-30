from flask import Flask, request, redirect, session
from datetime import datetime
import sqlite3
import calendar

app = Flask(__name__)
app.secret_key = "syoko_secret_key"
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = True

DB = "money.db"

# 支出カテゴリ
EXPENSE_CATEGORIES = [
    "⑧租税公課",
    "⑨荷造運賃",
    "⑩水道光熱費",
    "⑪旅費交通費",
    "⑫通信費",
    "⑬広告宣伝費",
    "⑭接待交通費",
    "⑮損害保険費",
    "⑯修繕費",
    "⑰消耗品費"
]


# =========================
# DB初期化
# =========================
def init_db():

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            user_type TEXT,
            customer TEXT,
            income INTEGER,
            income_note TEXT,
            expense_category TEXT,
            expense INTEGER,
            expense_note TEXT
        )
    """)

    conn.commit()
    conn.close()

init_db()

# =========================
# ログイン
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        password = request.form.get("password")

        if password == "0625":
            session["user_type"] = "SYOKO"
            print("LOGIN OK SYOKO")
            print(dict(session))
            return redirect("/")

        elif password == "0000":
            session["user_type"] = "guest"
            print("LOGIN OK GUEST")
            print(dict(session))
            return redirect("/")

        else:
            return """
            <h2>パスワードが違います</h2>
            <a href='/login'>戻る</a>
            """

    return """
    <body style="
        background:#d0f0ff;
        font-family:Arial;
        padding:30px;
    ">

    <div style="
        background:white;
        padding:20px;
        border-radius:15px;
    ">

        <h2>ログイン</h2>

        <form method="post">

            <input
                type="password"
                name="password"
                placeholder="パスワード"

                style="
                width:100%;
                padding:12px;
                margin-bottom:10px;
                border-radius:10px;
                border:1px solid #ccc;
                box-sizing:border-box;
                ">

            <button style="
                width:100%;
                padding:12px;
                background:#4da6ff;
                color:white;
                border:none;
                border-radius:10px;
            ">
                ログイン
            </button>

        </form>

    </div>

    </body>
    """


# =========================
# ホーム
# =========================
@app.route("/")
def home():
    print("SESSION =", dict(session))

    user_type = session.get("user_type")

    if not user_type:
        return redirect("/login")

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    month = request.args.get("month")

    if not month:
        month = datetime.now().strftime("%Y-%m")

    selected_date = request.args.get("date")

    year_select = request.args.get("year")


    # =========================
    # 月データ
    # =========================
    c.execute("""
    SELECT * FROM records
    WHERE date LIKE ?
    AND user_type = ?
    """, (f"{month}%", user_type))

    month_records = c.fetchall()

    total_month_income = sum(r[4] for r in month_records)
    total_month_expense = sum(r[7] for r in month_records)

    # =========================
    # 月内訳
    # =========================
    month_expense_detail = {}

    for category in EXPENSE_CATEGORIES:
        month_expense_detail[category] = 0

    for r in month_records:

        category = r[5]
        expense = r[6]

        if category in month_expense_detail:
            month_expense_detail[category] += expense

    # =========================
    # 年データ
    # =========================
    year_income = 0
    year_expense = 0

    year_expense_detail = {}

    for category in EXPENSE_CATEGORIES:
        year_expense_detail[category] = 0

    if year_select:

        c.execute("""
            SELECT * FROM records
            WHERE date LIKE ?
            AND user_type = ?
        """, (f"{year_select}%", user_type))

        year_records = c.fetchall()

        year_income = sum(r[4] for r in year_records)
        year_expense = sum(r[7] for r in year_records)

        for r in year_records:

            category = r[5]
            expense = r[6]

            if category in year_expense_detail:
                year_expense_detail[category] += expense

    # =========================
    # カレンダー用
    # =========================
    data = {}

    for r in month_records:

        d = r[1]

        if d not in data:
            data[d] = {
                "income": 0,
                "expense": 0
            }

        data[d]["income"] += r[4]
        data[d]["expense"] += r[7]

    # =========================
    # 日別
    # =========================
    day_records = []

    if selected_date:

        c.execute("""
            SELECT * FROM records
            WHERE date = ?
            AND user_type = ?
        """, (selected_date, user_type))

        day_records = c.fetchall()

    conn.close()

    year, mon = map(int, month.split("-"))

    cal = calendar.monthcalendar(year, mon)

    # =========================
    # HTML
    # =========================
    html = f"""
    <head>

        <meta name="viewport"
              content="width=device-width, initial-scale=1.0">

    </head>

    <body style="
        background:#d0f0ff;
        font-family:Arial;
        padding:10px;
        margin:0;
    ">

    <h1 style="
        text-align:center;
        font-size:28px;
    ">
        収支カレンダー
    </h1>

    <form method="get"
          style="
          background:white;
          padding:15px;
          border-radius:15px;
          margin-bottom:15px;
          ">

        <div style="margin-bottom:10px;">

            <input type="month"
                   name="month"
                   value="{month}"

                   style="
                   width:100%;
                   padding:12px;
                   font-size:16px;
                   border-radius:10px;
                   border:1px solid #ccc;
                   box-sizing:border-box;
                   ">

        </div>

        <button style="
            width:100%;
            padding:12px;
            font-size:18px;
            background:#4da6ff;
            color:white;
            border:none;
            border-radius:10px;
            margin-bottom:10px;
        ">
            月変更
        </button>

        <select name="year"

                style="
                width:100%;
                padding:12px;
                font-size:16px;
                border-radius:10px;
                border:1px solid #ccc;
                box-sizing:border-box;
                margin-bottom:10px;
                ">

            <option value="">年選択</option>

            <option value="2025">2025</option>
            <option value="2026">2026</option>
            <option value="2027">2027</option>
            <option value="2028">2028</option>
            <option value="2029">2029</option>
            <option value="2030">2030</option>

        </select>

        <button style="
            width:100%;
            padding:12px;
            font-size:18px;
            background:#ffb84d;
            color:white;
            border:none;
            border-radius:10px;
        ">
            年計算
        </button>

    </form>

    <!-- 月合計 -->
    <div style="
        background:white;
        padding:15px;
        border-radius:15px;
        margin-bottom:15px;
    ">

        <h2 style="margin-top:0;">
            {month} の合計
        </h2>

        <div style="
            color:green;
            font-size:20px;
            margin-bottom:8px;
        ">
            収入：{total_month_income}円
        </div>

        <div style="
            color:red;
            font-size:20px;
            margin-bottom:15px;
        ">
            支出：{total_month_expense}円
        </div>

        <b>内訳</b><br><br>
    """

    # 月内訳
    for k, v in month_expense_detail.items():

        html += f"""
        <div style="margin-bottom:5px;">
            {k}：{v}円
        </div>
        """

    html += "</div>"

    # =========================
    # 年表示
    # =========================
    if year_select:

        html += f"""
        <div style="
            background:#fff3cd;
            padding:15px;
            border-radius:15px;
            margin-bottom:15px;
        ">

            <h2 style="margin-top:0;">
                {year_select} 年の合計
            </h2>

            <div style="
                color:green;
                font-size:20px;
                margin-bottom:8px;
            ">
                収入：{year_income}円
            </div>

            <div style="
                color:red;
                font-size:20px;
                margin-bottom:15px;
            ">
                支出：{year_expense}円
            </div>

            <b>内訳</b><br><br>
        """

        for k, v in year_expense_detail.items():

            html += f"""
            <div style="margin-bottom:5px;">
                {k}：{v}円
            </div>
            """

        html += "</div>"

    # =========================
    # カレンダー
    # =========================
    html += """
    <div style="
        overflow-x:auto;
        margin-bottom:20px;
    ">
    """

    html += """
    <table border="1"
           cellpadding="8"

           style="
           background:white;
           border-collapse:collapse;
           width:100%;
           min-width:700px;
           ">
    """

    html += """
    <tr style="background:#4da6ff;color:white;">
        <th>月</th>
        <th>火</th>
        <th>水</th>
        <th>木</th>
        <th>金</th>
        <th>土</th>
        <th>日</th>
    </tr>
    """

    for week in cal:

        html += "<tr>"

        for day in week:

            if day == 0:

                html += "<td></td>"

            else:

                d_str = f"{month}-{day:02d}"

                income = data.get(d_str, {}).get("income", 0)
                expense = data.get(d_str, {}).get("expense", 0)

                html += f"""
                <td style="
                    vertical-align:top;
                    height:90px;
                    font-size:14px;
                ">

                    <a href="/?month={month}&date={d_str}"
                       style="
                       text-decoration:none;
                       color:black;
                       ">

                        <b style="font-size:18px;">
                            {day}
                        </b><br>

                        <div style="color:green;">
                            +{income}
                        </div>

                        <div style="color:red;">
                            -{expense}
                        </div>

                    </a>

                </td>
                """

        html += "</tr>"

    html += "</table></div>"

    # =========================
    # 日別管理
    # =========================
    if selected_date:

        html += f"""
        <div style="
            background:white;
            padding:15px;
            border-radius:15px;
            margin-bottom:20px;
        ">

        <h2>
            {selected_date}
        </h2>

        <form action="/add?date={selected_date}&month={month}"
              method="post">

            <input name="customer"
                   placeholder="お客さん"

                   style="
                   width:100%;
                   padding:12px;
                   margin-bottom:10px;
                   border-radius:10px;
                   border:1px solid #ccc;
                   box-sizing:border-box;
                   ">

            <input name="income"
                   type="number"
                   placeholder="収入"

                   style="
                   width:100%;
                   padding:12px;
                   margin-bottom:10px;
                   border-radius:10px;
                   border:1px solid #ccc;
                   box-sizing:border-box;
                   ">

            <input name="income_note"
                   placeholder="収入メモ"

                   style="
                   width:100%;
                   padding:12px;
                   margin-bottom:15px;
                   border-radius:10px;
                   border:1px solid #ccc;
                   box-sizing:border-box;
                   ">

            <select name="expense_category"

                    style="
                    width:100%;
                    padding:12px;
                    margin-bottom:10px;
                    border-radius:10px;
                    border:1px solid #ccc;
                    box-sizing:border-box;
                    ">
        """

        for category in EXPENSE_CATEGORIES:
            html += f"<option>{category}</option>"

        html += """
            </select>

            <input name="expense"
                   type="number"
                   placeholder="支出"

                   style="
                   width:100%;
                   padding:12px;
                   margin-bottom:10px;
                   border-radius:10px;
                   border:1px solid #ccc;
                   box-sizing:border-box;
                   ">

            <input name="expense_note"
                   placeholder="支出メモ"

                   style="
                   width:100%;
                   padding:12px;
                   margin-bottom:15px;
                   border-radius:10px;
                   border:1px solid #ccc;
                   box-sizing:border-box;
                   ">

            <button style="
                width:100%;
                padding:14px;
                font-size:18px;
                background:#4da6ff;
                color:white;
                border:none;
                border-radius:10px;
            ">
                追加
            </button>

        </form>

        </div>
        """

        incomes = []
        expenses = []

        for r in day_records:

            if r[4] > 0:
                incomes.append(r)

            if r[7] > 0:
                expenses.append(r)

        # 収入一覧
        html += """
        <div style="
            background:white;
            padding:15px;
            border-radius:15px;
            margin-bottom:15px;
        ">
        """

        html += "<h3>収入</h3>"

        if incomes:

            for r in incomes:

                html += f"""
                <div style="
                    border-bottom:1px solid #ddd;
                    padding:10px 0;
                ">

                    <b>{r[3]}</b><br>

                    {r[4]}円<br>

                    {r[5]}<br><br>

                    <a href="/edit/{r[0]}?date={selected_date}&month={month}">
                        編集
                    </a>

                    |

                    <a href="/delete/{r[0]}?date={selected_date}&month={month}">
                        削除
                    </a>

                </div>
                """

        else:
            html += "<p>なし</p>"

        total_income = sum(int(r[4]) for r in incomes)

        html += f"""
        <hr>
        <b>収入合計：{total_income}円</b>
        </div>
        """

        # 支出一覧
        html += """
        <div style="
            background:white;
            padding:15px;
            border-radius:15px;
            margin-bottom:15px;
        ">
        """

        html += "<h3>支出</h3>"

        if expenses:

            for r in expenses:

                html += f"""
                <div style="
                    border-bottom:1px solid #ddd;
                    padding:10px 0;
                ">

                    <b>{r[6]}</b><br>

                    {r[7]}円<br>

                    {r[8]}<br><br>

                    <a href="/edit/{r[0]}?date={selected_date}&month={month}">
                        編集
                    </a>

                    |

                    <a href="/delete/{r[0]}?date={selected_date}&month={month}">
                        削除
                    </a>

                </div>
                """

        else:
            html += "<p>なし</p>"

        total_expense = sum(int(r[7]) for r in expenses)

        html += f"""
        <hr>
        <b>支出合計：{total_expense}円</b>
        </div>
        """

    html += "</body>"

    return html


# =========================
# 追加
# =========================
@app.route("/add", methods=["POST"])
def add():

    selected_date = request.args.get("date")
    month = request.args.get("month")

    user_type = session.get("user_type")

    customer = request.form.get("customer")

    income = request.form.get("income") or 0

    income_note = request.form.get("income_note")

    expense_category = request.form.get("expense_category")

    expense = request.form.get("expense") or 0

    expense_note = request.form.get("expense_note")

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
        INSERT INTO records (
            date,
            user_type,
            customer,
            income,
            income_note,
            expense_category,
            expense,
            expense_note
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        selected_date,
        user_type,
        customer,
        int(income),
        income_note,
        expense_category,
        int(expense),
        expense_note
    ))

    conn.commit()
    conn.close()

    return redirect(f"/?date={selected_date}&month={month}")


# =========================
# 削除
# =========================
@app.route("/delete/<int:id>")
def delete(id):

    selected_date = request.args.get("date")
    month = request.args.get("month")

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("DELETE FROM records WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect(f"/?date={selected_date}&month={month}")


# =========================
# 編集画面
# =========================
@app.route("/edit/<int:id>")
def edit(id):

    selected_date = request.args.get("date")
    month = request.args.get("month")

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("SELECT * FROM records WHERE id=?", (id,))

    r = c.fetchone()

    conn.close()

    return f"""
    <head>

        <meta name="viewport"
              content="width=device-width, initial-scale=1.0">

    </head>

    <body style="
        font-family:Arial;
        background:#d0f0ff;
        padding:15px;
    ">

    <div style="
        background:white;
        padding:20px;
        border-radius:15px;
    ">

    <h2>編集</h2>

    <form action="/update/{id}?date={selected_date}&month={month}"
          method="post">

        <input name="customer"
               value="{r[3]}"

               style="
               width:100%;
               padding:12px;
               margin-bottom:10px;
               border-radius:10px;
               border:1px solid #ccc;
               box-sizing:border-box;
               ">

        <input name="income"
               value="{r[4]}"

               style="
               width:100%;
               padding:12px;
               margin-bottom:10px;
               border-radius:10px;
               border:1px solid #ccc;
               box-sizing:border-box;
               ">

        <input name="income_note"
               value="{r[5]}"

               style="
               width:100%;
               padding:12px;
               margin-bottom:10px;
               border-radius:10px;
               border:1px solid #ccc;
               box-sizing:border-box;
               ">

        <input name="expense_category"
               value="{r[6]}"

               style="
               width:100%;
               padding:12px;
               margin-bottom:10px;
               border-radius:10px;
               border:1px solid #ccc;
               box-sizing:border-box;
               ">

        <input name="expense"
               value="{r[7]}"

               style="
               width:100%;
               padding:12px;
               margin-bottom:10px;
               border-radius:10px;
               border:1px solid #ccc;
               box-sizing:border-box;
               ">

        <input name="expense_note"
               value="{r[8]}"

               style="
               width:100%;
               padding:12px;
               margin-bottom:15px;
               border-radius:10px;
               border:1px solid #ccc;
               box-sizing:border-box;
               ">

        <button style="
            width:100%;
            padding:14px;
            font-size:18px;
            background:#4da6ff;
            color:white;
            border:none;
            border-radius:10px;
        ">
            更新
        </button>

    </form>

    </div>

    </body>
    """


# =========================
# 更新
# =========================
@app.route("/update/<int:id>", methods=["POST"])
def update(id):

    selected_date = request.args.get("date")
    month = request.args.get("month")

    customer = request.form.get("customer")

    income = request.form.get("income") or 0

    income_note = request.form.get("income_note")

    expense_category = request.form.get("expense_category")

    expense = request.form.get("expense") or 0

    expense_note = request.form.get("expense_note")

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
        UPDATE records
        SET
            customer=?,
            income=?,
            income_note=?,
            expense_category=?,
            expense=?,
            expense_note=?
        WHERE id=?
    """, (
        customer,
        int(income),
        income_note,
        expense_category,
        int(expense),
        expense_note,
        id
    ))

    conn.commit()
    conn.close()

    return redirect(f"/?date={selected_date}&month={month}")


import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)