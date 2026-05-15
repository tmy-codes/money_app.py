from flask import Flask, request, redirect
import sqlite3

app = Flask(__name__)

DB = "todo.db"


# データベース初期化
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            done INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

init_db()


@app.route("/")
def home():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT id, text, done FROM tasks")
    tasks = c.fetchall()
    conn.close()

    html = """
    <h1>ToDoアプリ（SQLite保存版）</h1>

    <form action="/add" method="post">
        <input type="text" name="task">
        <button type="submit">追加</button>
    </form>

    <ul>
    """

    for t in tasks:
        task_id = t[0]
        text = t[1]
        done = t[2]

        style = "text-decoration: line-through;" if done else ""

        html += f"""
        <li style="{style}">
            {text}
            <a href="/toggle/{task_id}">[完了]</a>
            <a href="/delete/{task_id}">[削除]</a>
        </li>
        """

    html += "</ul>"
    return html


@app.route("/add", methods=["POST"])
def add():
    task = request.form.get("task")

    if task:
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("INSERT INTO tasks (text, done) VALUES (?, ?)", (task, 0))
        conn.commit()
        conn.close()

    return redirect("/")


@app.route("/toggle/<int:task_id>")
def toggle(task_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("SELECT done FROM tasks WHERE id = ?", (task_id,))
    current = c.fetchone()

    if current:
        new_value = 0 if current[0] == 1 else 1
        c.execute("UPDATE tasks SET done = ? WHERE id = ?", (new_value, task_id))

    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/delete/<int:task_id>")
def delete(task_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

    conn.commit()
    conn.close()

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)