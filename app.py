import os
import sys
import logging
from pathlib import Path
from datetime import timedelta
from contextlib import contextmanager


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from dotenv import load_dotenv
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash
)


from modules.db import get_connection
from modules.db_links import create_link, list_links, remove_link, db_cursor
from modules.generate_barcode import generate_ean13


load_dotenv(Path(__file__).with_name(".env"))

logging.basicConfig(
    filename="logs.txt",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret")
app.permanent_session_lifetime = timedelta(minutes=30)


def is_logged_in() -> bool:
    """Return True if the current session is authenticated."""
    return "username" in session


def login_required(view_func):
    """Redirect to /login when the user is not authenticated."""
    def wrapper(*args, **kwargs):
        if not is_logged_in():
            flash("You must log in first.", "warning")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper




@app.route("/login", methods=["GET", "POST"])
def login():
    """Sign-in page: authenticates against sec_users."""
    if is_logged_in():
        return redirect(url_for("home"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Please fill in all fields.", "error")
            return render_template("login.html")

        try:
            conn = get_connection()
            cur = conn.cursor(dictionary=True)
            cur.execute("""
                SELECT
                    user_id, username, password, First_name, last_name,
                    active, mobile_user, pincode
                FROM sec_users
                WHERE username = %s
                LIMIT 1
            """, (username,))
            user = cur.fetchone()
            conn.close()
        except Exception as e:
            logging.exception("Database error while logging in")
            flash("Database connection error.", "error")
            return render_template("login.html")

        if not user:
            flash("Invalid username or password.", "error")
            return render_template("login.html")

        if int(user.get("active", 0)) != 1:
            flash("Your account is inactive.", "error")
            return render_template("login.html")

        valid_password = password == (user.get("password") or "")
        valid_pincode = (
            int(user.get("mobile_user") or 0) == 1
            and password == str(user.get("pincode") or "")
        )

        if not (valid_password or valid_pincode):
            flash("Invalid password or pincode.", "error")
            return render_template("login.html")

        session.permanent = True
        session.update({
            "user_id": user["user_id"],
            "username": user["username"],
            "first_name": user.get("First_name", ""),
            "last_name": user.get("last_name", "")
        })
        logging.info(f"User '{username}' logged in successfully.")
        return redirect(url_for("home"))


    """Clear the session and return to login."""
    user = session.get("username", "unknown")
    session.clear()
    logging.info(f"User '{user}' logged out.")
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route("/")
@login_required
def home():
    """Landing page after login."""
    return render_template(
        "home.html",
        username=session.get("username"),
        first_name=session.get("first_name"),
        last_name=session.get("last_name"),
    )


@app.route("/scan", methods=["GET", "POST"])
@login_required
def scan():
    """
    Scan page.
    - GET: renders the page with two scanners (barcode + location).
    - POST: manually processes a single 'barcode' field.
    """
    if request.method == "POST":
        barcode = (request.form.get("barcode") or "").strip()
        if not barcode:
            flash("Please provide a barcode.", "error")
        else:
            flash(f"Scanned: {barcode}", "success")

    return render_template("scan.html")


@app.post("/link-scanned")
@login_required
def link_scanned():
    """Handles linking a scanned barcode to a location."""
    barcode = request.form.get("barcode", "").strip()
    location = request.form.get("location", "").strip()

    if not barcode or not location:
        flash("Both barcode and location are required.", "error")
        return redirect(url_for("scan"))

    try:
        with db_cursor() as (conn, cur):
            cur.execute("""
                INSERT INTO linked_items (barcode, location, user_id)
                VALUES (%s, %s, %s)
            """, (barcode, location, session.get("user_id")))
        flash(f"Linked {barcode} → {location}", "success")
    except Exception:
        logging.exception("DB error while linking barcode.")
        flash("Could not save the link (DB error).", "error")

    return redirect(url_for("scan"))


@app.route("/generate-barcode")
@login_required
def generate_barcode():
    """Generate a demo EAN-13 barcode into /static/ (PNG)."""
    try:
        generate_ean13("123456789102", "ean13_barcode", session["username"])
        flash("Barcode generated successfully.", "success")
        return "Barcode generated and saved in /static/."
    except Exception:
        logging.exception("Error generating barcode")
        flash("An error occurred while generating the barcode.", "error")
        return "An error occurred while generating the barcode.", 500


@app.route("/users")
@login_required
def users():
    """Shows a list of active users."""
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT user_id, username, First_name AS first_name, last_name, active, mobile_user
            FROM sec_users
            WHERE active = 1
            ORDER BY username
        """)
        users = cur.fetchall()
        conn.close()
        return render_template("users.html", users=users)
    except Exception:
        logging.exception("Database error while fetching users.")
        flash("Database error while fetching users.", "error")
        return redirect(url_for("home"))


@app.route("/locations", methods=["GET", "POST"])
@login_required
def locations():
    """
    Location management:
    - GET: shows existing links (optionally filtered by location)
    - POST: adds a new barcode → location link
    """
    q_loc = (request.args.get("location") or "").strip()

    if request.method == "POST":
        location = (request.form.get("location") or "").strip()
        barcode = (request.form.get("barcode") or "").strip()

        if not location or not barcode:
            flash("Both barcode and location are required.", "error")
            return redirect(url_for("locations", location=q_loc or None))

        try:
            added = create_link(barcode, location, session.get("user_id"))
            msg = f"Linked {barcode} → {location}"
            if not added:
                msg += " (already exists)"
            flash(msg, "success")
        except Exception:
            logging.exception("DB error while linking barcode to location.")
            flash("Could not save the link (DB error).", "error")

        return redirect(url_for("locations", location=location))

  
    rows, suggested_locations, raw_loc_ids = [], [], []
    try:
        with db_cursor() as (conn, cur):
            cur.execute("""
                SELECT location, COUNT(*) AS n
                FROM linked_items
                WHERE location IS NOT NULL AND location <> ''
                GROUP BY location
                ORDER BY n DESC, location ASC
                LIMIT 200
            """)
            suggested_locations = [r["location"] for r in cur.fetchall()]

            cur.execute("SELECT locatie_id FROM mgz_inhoud_product_locations ORDER BY locatie_id LIMIT 200")
            raw_loc_ids = [str(r["locatie_id"]) for r in cur.fetchall()]

        rows = list_links(q_loc)
    except Exception:
        logging.exception("Database read error on /locations.")
        flash("Database error while loading links.", "error")

    return render_template(
        "locations.html",
        rows=rows,
        suggested_locations=suggested_locations,
        raw_loc_ids=raw_loc_ids,
        q_loc=q_loc,
    )


@app.post("/locations/remove")
@login_required
def locations_remove():
    """Removes a barcode-location link."""
    rid = (request.form.get("id") or "").strip()
    barcode = (request.form.get("barcode") or "").strip()
    location = (request.form.get("location") or "").strip()

    try:
        remove_link(id=rid or None, barcode=barcode or None, location=location or None)
        flash("Link removed.", "success")
    except Exception:
        logging.exception("Database error while removing link.")
        flash("Could not remove link (Database error).", "error")

    return redirect(url_for("locations", location=location or None))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
