from dotenv import load_dotenv
import os
from flask import Flask, render_template, request, redirect, url_for, session
from modules.db import get_connection
from modules.generate_barcode import generate_ean13
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import timedelta
import logging

load_dotenv() 
logging.basicConfig(filename='logs.txt', level=logging.ERROR)

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.permanent_session_lifetime = timedelta(minutes=30)


@app.route("/login", methods=["GET", "POST"])
def login():
    if "username" in session:
        return redirect(url_for("home"))

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            conn.close()
        except Exception as e:
            logging.error(f"Database connection error: {e}")
            return render_template("login.html", error="There is a problem with the database.")

        if user and check_password_hash(user["password"], password):
            session.permanent = True
            session["username"] = user["username"]
            session["role"] = user["role"]
            return redirect(url_for("home"))
        else:
            return render_template("login.html", error="Login failed. Check username and password.")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if "username" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]

        allowed_roles = ["scanner", "admin", "viewer"]
        if role not in allowed_roles:
            return render_template("register.html", message="Invalid role selected.")

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                (username, generate_password_hash(password), role)
            )
            conn.commit()
            conn.close()
            message = f"User {username} successfully registered!"
        except Exception as e:
            logging.error(f"Error registering user: {e}")
            message = f"Registration failed for {username}."

        return render_template("register.html", message=message)

    return render_template("register.html")


@app.route("/")
def home():
    if not session.get("username"):
        return redirect(url_for("login"))
    return render_template("home.html", username=session["username"])


@app.route("/scan")
def scan():
    if not session.get("username"):
        return redirect(url_for("login"))
    return render_template("scan.html")


@app.route("/generate-barcode")
def generate_barcode():
    if not session.get("username"):
        return redirect(url_for("login"))
    
    generate_ean13("123456789102", "ean13_barcode", session["username"])
    return "Barcode generated and saved in /static/"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", ssl_context="adhoc")
