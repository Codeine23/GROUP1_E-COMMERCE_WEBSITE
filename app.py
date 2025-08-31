import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from dotenv import load_dotenv 
from data.dummy_data import products


load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
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

@app.context_processor
def inject_user():
    return dict(
        username=session.get("username"),
        is_admin=session.get("role") == "admin"
    )
# -------- DATABASE CONNECTION --------
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row 
    return conn

with get_db_connection() as conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()

 

# -------- ROUTES --------
@app.route("/")
def home():
    # Filter for featured products
    featured = [p for p in products if "featured" in p.get("tags", [])]

    # Filter for best sellers
    best_sellers = [p for p in products if "best_seller" in p.get("tags", [])]

    return render_template(
        "pages/home.html",
        username=session.get("username"),
        featured=featured,
        best_sellers=best_sellers
    )

@app.route("/best-selling")
def best_selling():
    # default filter is last30
    period = request.args.get("period", "last30")

    # sort/filter products by the chosen period
    sorted_products = sorted(
        products,
        key=lambda p: p["sold"][period],
        reverse=True  # highest sold first
    )

    return render_template(
        "pages/best_selling.html",
        products=sorted_products,
        period=period
    )


@app.route("/cart")
@login_required
def cart():
    return render_template("pages/cart.html")


@app.route("/checkout")
@login_required
def checkout():
    return render_template("pages/checkout.html")

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


#------------ AUTH ------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            session.clear()
            session["username"] = ADMIN_EMAIL
            session["is_admin"] = True
            flash("Welcome admin!", "success")
            return redirect(url_for("admin_dashboard"))

        elif not email or not password:
            flash("Username and password are required.", "danger")
            return redirect(url_for("login"))

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
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
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('register'))

        
        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (email, username, password) VALUES (?, ?, ?)',
                         (email, username, hashed_password))
            conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError as e:
            if "email" in str(e).lower():
                flash('Email already exists. Choose another.', 'danger')
            else:
                flash('An error occurred. Please try again.', 'danger')
            return redirect(url_for('register'))
        finally:
            conn.close()
    return render_template("auth/register.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))


# -------- ADMIN ROUTES --------
"""
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
"""

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("is_admin"):
            flash("Admin access only.", "danger")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    conn = get_db_connection()
    users = conn.execute("SELECT id, username, email, password FROM users").fetchall()
    conn.close()
    return render_template("admin/dashboard.html", users=users)


@app.route("/admin/delete_user/<int:user_id>", methods=["POST", "GET"])
@admin_required
def delete_user(user_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    flash("User deleted successfully.", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/add_product")
def add_product():
    return render_template("admin/add_product.html")

@app.route("/admin/manage_users")
def manage_users():
    return render_template("admin/manage_users.html")





if __name__ == "__main__":
    app.run(debug=True)