import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from dotenv import load_dotenv 


load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
DB_NAME = os.getenv("DB_NAME")


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('You need to log in first.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# -------- DATABASE CONNECTION --------
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row 
    return conn

with get_db_connection() as conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()

 

# -------- ROUTES --------
@app.route("/")
def home():
    return render_template("pages/home.html", username=session.get("username"))

@app.route("/best-selling")
def best_selling():
    return render_template("pages/best_selling.html")

@app.route("/cart")
@login_required
def cart():
    return render_template("pages/cart.html")

@app.route("/contact-us")
def contact():
    return render_template("pages/contact_us.html")

@app.route("/gadgets")
def gadget():
    return render_template("pages/gadgets.html")

@app.route("/about")
def about():
    return render_template("pages/about.html")

@app.route("/last30days")
def last_days():
    return render_template("pages/last30days.html")

#----------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Username and password are required.", "danger")
            return redirect(url_for("login"))

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["is_admin"] = False
            flash("Login successful!", "success")
            return redirect(url_for("home"))

        flash("Invalid username or password.", "danger")
        return redirect(url_for("login"))

    return render_template("auth/login.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('register'))

        
        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                         (username, hashed_password))
            conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists. Choose another.', 'danger')
            return redirect(url_for('register'))
        finally:
            conn.close()
    return render_template("auth/register.html")



@app.route("/shoes")
def shoes():
    return render_template("pages/shoes.html")

@app.route("/wishlist")
@login_required
def wishlist():
    return render_template("pages/wishlist.html")

@app.route("/men_clothings")
def men():
    return render_template("pages/men_clothings.html")

@app.route("/women_clothings")
def women():
    return render_template("pages/women_clothings.html")

@app.route("/search")
def search():
    query = request.args.get("q")
    return f"Search results for: {query}"


# -------- ADMIN ROUTES --------
@app.route("/admin/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session.clear()
            session["is_admin"] = True
            session["username"] = ADMIN_USERNAME
            flash("Admin login successful.", "success")
            return redirect(url_for("admin_dashboard"))

        flash("Invalid admin credentials.", "danger")
        return redirect(url_for("admin_login"))

    return render_template("admin/admin_login.html")


@app.route("/admin/dashboard")
def admin_dashboard():
    return render_template("admin/dashboard.html")

@app.route("/admin/add_product")
def add_product():
    return render_template("admin/add_product.html")

@app.route("/admin/manage_users")
def manage_users():
    return render_template("admin/manage_users.html")





if __name__ == "__main__":
    app.run(debug=True)
