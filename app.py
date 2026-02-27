import sqlite3

def init_db():
    conn = sqlite3.connect("quiz.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'user'
    )
    """)

    conn.commit()
    conn.close()

init_db()
# =========================
# IMPORTS
# =========================
from flask import Flask, render_template, request, redirect, session
from flask_wtf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

import os
import json
import random
import sqlite3

# =========================
# APP SETUP
# =========================
app = Flask(__name__)
app.secret_key = "quiz_secret"
csrf = CSRFProtect(app)

# =========================
# DATABASE HELPER
# =========================
def get_db():
    return sqlite3.connect("quiz.db")

# =========================
# ADMIN DECORATOR
# =========================
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            return redirect("/login")
        if session.get("role") != "admin":
            return "Access denied ❌"
        return f(*args, **kwargs)
    return decorated_function

# =========================
# LOAD QUESTIONS FROM JSON
# =========================
def load_questions():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "data", "questions.json")

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_questions(questions):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "data", "questions.json")

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(questions, f, indent=4)

# =========================
# USER ROUTES
# =========================
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        fullname = request.form["fullname"]
        username = request.form["username"]
        email = request.form["email"]
        age = int(request.form["age"])
        password = request.form["password"]

        if len(password) < 8:
            return "Password must be at least 8 characters long"

        hashed_pw = generate_password_hash(password)

        db = get_db()
        try:
            db.execute(
                "INSERT INTO users VALUES (?,?,?,?,?,?)",
                (username, hashed_pw, fullname, email, age, "user")
            )
            db.commit()
        except sqlite3.IntegrityError:
            return "Username already exists"

        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        user = db.execute(
            "SELECT password, role FROM users WHERE username=?",
            (username,)
        ).fetchone()

        if user is None:
            return render_template("login.html", error="Invalid credentials")

        if not check_password_hash(user[0], password):
            return render_template("login.html", error="Invalid credentials")

        session["username"] = username
        session["role"] = user[1]

        return redirect("/quiz")

    return render_template("login.html")


@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    if "username" not in session:
        return redirect("/login")

    all_questions = load_questions()

    if request.method == "POST":
        year_range = request.form["year_range"]
        start, end = map(int, year_range.split("-"))

        filtered = [q for q in all_questions if start <= q["year"] <= end]

        if not filtered:
            return "No questions available for this year range."

        selected = random.sample(filtered, min(10, len(filtered)))
        session["quiz_questions"] = selected

        return redirect("/start_quiz")

    return render_template("select_year.html")


@app.route("/start_quiz")
def start_quiz():
    questions = session.get("quiz_questions", [])
    return render_template("quiz.html", questions=questions)


@app.route("/result", methods=["POST"])
def result():
    score = 0
    questions = session.get("quiz_questions", [])

    for q in questions:
        selected = request.form.get(str(q["id"]))
        if selected == q["answer"]:
            score += 1

    return render_template("result.html", score=score, total=len(questions))


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# =========================
# ADMIN ROUTES
# =========================
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        admin = db.execute(
            "SELECT password FROM users WHERE username=? AND role='admin'",
            (username,)
        ).fetchone()

        if admin and check_password_hash(admin[0], password):
            session["username"] = username
            session["role"] = "admin"
            return redirect("/admin/dashboard")

        return render_template("admin/admin_login.html", error="Invalid admin credentials")

    return render_template("admin/admin_login.html")


@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    db = get_db()
    total_users = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]

    return render_template("admin/dashboard.html", total_users=total_users)


# =========================
# MANAGE USERS
# =========================
@app.route("/admin/users")
@admin_required
def admin_users():
    db = get_db()
    users = db.execute(
        "SELECT username, email, role FROM users"
    ).fetchall()
    return render_template("admin/manage_users.html", users=users)


@app.route("/admin/make_admin/<username>")
@admin_required
def make_admin(username):
    db = get_db()
    db.execute(
        "UPDATE users SET role='admin' WHERE username=?",
        (username,)
    )
    db.commit()
    return redirect("/admin/users")


# =========================
# MANAGE QUESTIONS
# =========================
@app.route("/admin/questions", methods=["GET", "POST"])
@admin_required
def admin_questions():
    questions = load_questions()

    if request.method == "POST":
        new_question = {
            "id": len(questions) + 1,
            "year": int(request.form["year"]),
            "question": request.form["question"],
            "options": [
                request.form["opt1"],
                request.form["opt2"],
                request.form["opt3"],
                request.form["opt4"],
            ],
            "answer": request.form["answer"]
        }

        questions.append(new_question)
        save_questions(questions)

        return redirect("/admin/questions")

    return render_template("admin/manage_questions.html", questions=questions)


@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect("/admin/login")


# =========================
# RUN APP
# =========================
if __name__ == "__main__":
    app.run(debug=True)