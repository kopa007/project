import sqlite3
from flask import Flask, redirect, render_template, request, session
from werkzeug.security import generate_password_hash, check_password_hash
import traceback

app = Flask(__name__)
app.secret_key = "secret_key"

@app.errorhandler(Exception)
def handle_error(e):
    print("\n\n===== ERROR TRACEBACK =====")
    traceback.print_exc()
    print("===== END TRACEBACK =====\n\n")
    return "Internal Server Error", 500

def get_db():
    conn = sqlite3.connect("finance.db")
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        hash_pw = generate_password_hash(password)
        db = get_db()

        try:
            db.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, hash_pw)
            )
            db.commit()
            return redirect("/login")
        except sqlite3.IntegrityError:
            return render_template("register.html", error="Username already exists")
    return render_template("register.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()


        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            return redirect("/dashboard")
        else:
            error = "Invalid username or password"
            return render_template("login.html", error=error)

    return render_template("login.html")


@app.route("/add", methods=["GET", "POST"])
def add_transaction():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")

    db = get_db()

    if request.method == "POST":
        amount = request.form["amount"]
        category = request.form["category"]
        t_type = request.form["type"]
        date = request.form["date"]
        desc = request.form["description"]

        db.execute(
            """INSERT INTO transactions
            (user_id, category_id, amount, type, date, description)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (session["user_id"], category, amount, t_type, date, desc)
        )
        db.commit()
        return redirect("/dashboard")

    categories = db.execute(
        "SELECT * FROM categories WHERE user_id = ? OR user_id IS NULL",
        (session["user_id"],)
    ).fetchall()
    categories = [dict(row) for row in categories]
    return render_template("add_transaction.html", categories=categories)


@app.route("/dashboard")
def dashboard():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")

    db = get_db()

    income = db.execute(
        "SELECT SUM(amount) FROM transactions WHERE user_id = ? AND type='income'",
        (user_id,)
    ).fetchone()[0] or 0

    expense = db.execute(
        "SELECT SUM(amount) FROM transactions WHERE user_id = ? AND type='expense'",
        (user_id,)
    ).fetchone()[0] or 0

    transactions = db.execute(
        """SELECT t.*, c.name AS category
           FROM transactions t
           LEFT JOIN categories c ON t.category_id = c.id
           WHERE t.user_id = ?
           ORDER BY t.date DESC""",
        (user_id,)
    ).fetchall()

    transactions = [dict(row) for row in transactions]

    return render_template(
        "dashboard.html",
        income=income,
        expense=expense,
        balance=income - expense,
        transactions=transactions
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/")
def index():
    return redirect("/dashboard")
