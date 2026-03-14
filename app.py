from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"


def db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def home():
    if "user" in session:
        return redirect("/tasks")
    return redirect("/login")


@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = db()
        cur = conn.cursor()

        user = cur.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username,password)
        ).fetchone()

        if user:
            session["user"] = user["id"]
            return redirect("/tasks")

    return render_template("login.html")


@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = db()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO users(username,password) VALUES(?,?)",
            (username,password)
        )

        conn.commit()

        return redirect("/login")

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/tasks")
def tasks():

    if "user" not in session:
        return redirect("/login")

    sort = request.args.get("sort")

    if sort == "date":
        order = "date ASC"
    elif sort == "alpha":
        order = "title COLLATE NOCASE ASC"
    else:
        order = "favorite DESC, completed ASC, id DESC"

    conn = db()
    cur = conn.cursor()

    tasks = cur.execute(
        f"""
        SELECT * FROM tasks
        WHERE user_id=?
        ORDER BY completed ASC, favorite DESC, {order}
        """,
        (session["user"],)
    ).fetchall()

    return render_template("tasks.html", tasks=tasks)


@app.route("/add_task", methods=["POST"])
def add_task():

    title = request.form["title"]
    date = request.form["date"]

    conn = db()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO tasks(user_id,title,date) VALUES(?,?,?)",
        (session["user"],title,date)
    )

    conn.commit()

    return redirect("/tasks")


@app.route("/favorite/<int:id>", methods=["POST"])
def favorite(id):

    conn = db()
    cur = conn.cursor()

    task = cur.execute(
        "SELECT favorite FROM tasks WHERE id=?",
        (id,)
    ).fetchone()

    new = 0 if task["favorite"] else 1

    cur.execute(
        "UPDATE tasks SET favorite=? WHERE id=?",
        (new,id)
    )

    conn.commit()

    return redirect("/tasks")


@app.route("/complete/<int:id>", methods=["POST"])
def complete(id):

    conn = db()
    cur = conn.cursor()

    task = cur.execute(
        "SELECT completed FROM tasks WHERE id=?",
        (id,)
    ).fetchone()

    new = 0 if task["completed"] else 1

    cur.execute(
        "UPDATE tasks SET completed=? WHERE id=?",
        (new,id)
    )

    conn.commit()

    return redirect("/tasks")


@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):

    conn = db()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM tasks WHERE id=?",
        (id,)
    )

    conn.commit()

    return redirect("/tasks")


@app.route("/update_description/<int:id>", methods=["POST"])
def update_description(id):

    description = request.form["description"]

    conn = db()
    cur = conn.cursor()

    cur.execute(
        "UPDATE tasks SET description=? WHERE id=?",
        (description,id)
    )

    conn.commit()

    return redirect("/tasks")


if __name__ == "__main__":
    app.run(debug=True)
