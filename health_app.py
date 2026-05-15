from flask import Flask, request, redirect
import sqlite3

app = Flask(__name__)
DB = "health.db"


def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            breakfast TEXT,
            lunch TEXT,
            dinner TEXT,
            exercise TEXT,
            duration TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()


@app.route("/")
def home():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM logs ORDER BY id DESC")
    logs = c.fetchall()
    conn.close()

    html = """
    <body style="background-color:#d0f0ff; font-family:Arial; padding:20px;">
    <h1>食事・運動記録アプリ</h1>

    <form action="/add" method="post">
        <p>日付: <input type="date" name="date"></p>
        <p>朝: <input type="text" name="breakfast"></p>
        <p>昼: <input type="text" name="lunch"></p>
        <p>夜: <input type="text" name="dinner"></p>
        <p>運動: <input type="text" name="exercise"></p>
        <p>時間: <input type="text" name="duration"></p>
        <button type="submit">保存</button>
    </form>

    <hr>
    """

    for l in logs:
        html += f"""
        <div style="margin-bottom:10px;">
            <b>{l[1]}</b><br>
            朝: {l[2]}<br>
            昼: {l[3]}<br>
            夜: {l[4]}<br>
            運動: {l[5]} ({l[6]})<br>
        </div>
        <hr>
        """

    html += "</body>"
    return html


@app.route("/add", methods=["POST"])
def add():
    date = request.form.get("date")
    breakfast = request.form.get("breakfast")
    lunch = request.form.get("lunch")
    dinner = request.form.get("dinner")
    exercise = request.form.get("exercise")
    duration = request.form.get("duration")

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        INSERT INTO logs (date, breakfast, lunch, dinner, exercise, duration)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (date, breakfast, lunch, dinner, exercise, duration))
    conn.commit()
    conn.close()

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)