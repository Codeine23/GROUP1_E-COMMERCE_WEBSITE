import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from dotenv import load_dotenv 
from data.dummy_data import products
from utils.wishlist import add_to_wishlist_helper, remove_from_wishlist_helper, get_wishlist_items
from utils.cart import add_to_cart, remove_from_cart, get_cart_items, update_quantity
from utils.products import get_product


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
        is_admin=session.get("role") == "admin",
        cart=session.get("cart", {}),
        wishlist=session.get("wishlist", {})
    )

# -------- DATABASE CONNECTION --------
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row 
    return conn

with get_db_connection() as conn:
    # Create users table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Create orders table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL,
            address TEXT NOT NULL,
            city TEXT NOT NULL,
            state TEXT NOT NULL,
            zipcode TEXT NOT NULL,
            total_amount REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

@app.route("/categories")
def categories():
    # get unique categories from your products dummy data
    categories = list({tag for p in products for tag in p.get("tags", [])})

    # get query param for category
    selected_category = request.args.get("category", "featured")

    if selected_category == "featured":
        filtered_products = [p for p in products if "featured" in p.get("tags", [])]
    else:
        filtered_products = [p for p in products if selected_category in p.get("tags", [])]

    return render_template(
        "pages/categories.html",
        categories=categories,
        products=filtered_products,
        selected_category=selected_category
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

@app.route("/product/<int:product_id>")
def product_detail(product_id):
    product = get_product(product_id)
    
    if not product:
        flash("Product not found.", "danger")
        return redirect(url_for("home"))
    
    related_products = []
    if product.get("tags"):
        main_tag = product["tags"][0] #only the first tag

        for p in products:
            if p["id"] != product["id"] and p.get("tags") and main_tag in p["tags"]:
                related_products.append(p)

    related_products = related_products[:4]

    return render_template(
        "pages/product_detail.html",
         product=product,
         related_products=related_products
         )


@app.route("/cart")
@login_required
def cart():
    cart_items_with_details, subtotal = get_cart_items()
    
    shipping = 5 if subtotal > 0 else 0
    total = subtotal + shipping

    return render_template(
        "pages/cart.html", cart_items=cart_items_with_details,
        subtotal=subtotal,
        shipping=shipping,
        total=total
    )


@app.route("/add_to_cart/<int:product_id>")
def add(product_id):
    add_to_cart(product_id)
    flash("Item added to cart", "success")
    return redirect(request.referrer or url_for('home'))


@app.route("/remove_from_cart/<int:product_id>")
def remove(product_id):
    remove_from_cart(product_id)
    flash("Item removed from cart", "info")
    return redirect(request.referrer or url_for('home'))

@app.route('/update_cart/<product_id>', methods=["POST"])
def update_cart(product_id):
    qty = int(request.form.get("quantity", 1))
    cart = session.get("cart", {})
    product_id = str(product_id)

    if qty > 0:
        cart[product_id] = qty
    else:
        cart.pop(product_id, None)
    session["cart"] = cart
    return redirect(url_for("cart"))

@app.route('/remove_from_cart/<product_id>', methods=["POST"])
def remove_from_cart(product_id):
    cart = session.get("cart", {})
    product_id = str(product_id)

    if product_id in cart:
        del cart[product_id]
    session["cart"] = cart

    return redirect(url_for("cart"))


@app.route("/update_quantity/<int:product_id>", methods=["POST"])
def update_quantity_route(product_id):
    quantity = int(request.form.get("quantity", 1))
    update_quantity(product_id, quantity)
    return jsonify(success=True, cart=session.get("cart", {}))


@app.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    cart_items_with_details, subtotal = get_cart_items()
    shipping = 5 if subtotal > 0 else 0
    total = subtotal + shipping

    if request.method == "POST":
        # ✅ Extract form data
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        address = request.form.get("address")
        city = request.form.get("city")
        state = request.form.get("state")
        zipcode = request.form.get("postcode")
        payment_method = request.form.get("payment")  # <-- must exist in your form

        # ✅ Save order into DB
        with get_db_connection() as conn:
            conn.execute(
                """
                INSERT INTO orders (
                    first_name, last_name, email, address, city, state, zipcode, total_amount
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (first_name, last_name, email, address, city, state, zipcode, total),
            )
            conn.commit()

        # ✅ Clear cart after saving
        session["cart"] = {}

        # ✅ handle redirection depending on payment
        if payment_method == "pod":
            # Pay on Delivery → go straight to confirmation page
            flash("Order placed successfully! Pay on Delivery selected.", "success")
            return redirect(url_for("order_confirmation"))
        else:
            # Bank Payment → fake gateway simulation page
            return redirect(url_for("pay_gateway"))

    return render_template(
        "pages/checkout.html",
        cart_items=cart_items_with_details,
        shipping=shipping,
        subtotal=subtotal,
        total=total,
    )


@app.route("/order-confirmation")
@login_required
def order_confirmation():
    return render_template("pages/order_confirmation.html")

@app.route("/pay-gateway", methods=["GET", "POST"])
def pay_gateway():
    if request.method == "POST":
        # fake verification logic
        card_number = request.form.get("card_number")
        if card_number and card_number.startswith("4"):  # e.g., "Visa starts with 4"
            flash("Payment successful!", "success")
            return redirect(url_for("order_confirmation"))
        else:
            flash("Payment failed! Try again.", "danger")
    return render_template("pages/pay_gateway.html")

@app.route("/wishlist")
@login_required
def wishlist():
    wishlist = get_wishlist_items()
    return render_template(
        "pages/wishlist.html",
        wishlist=wishlist
    )


@app.route("/wishlist/add/<int:product_id>", methods=["POST"])
@login_required
def add_to_wishlist(product_id):
    add_to_wishlist_helper(product_id)
    flash("Item added to your wishlist", "success")
    return redirect(request.referrer or url_for("wishlist"))

@app.route("/wishlist/remove/<int:product_id>", methods=["POST"])
@login_required
def remove_from_wishlist(product_id):
    remove_from_wishlist_helper(product_id)  # from wishlist.py
    flash("Item removed from wishlist", "info")
    return redirect(request.referrer or url_for("wishlist"))


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
            guest_cart = session.get("cart", {})
            guest_wishlist = session.get("wishlist", {})

            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["is_admin"] = False

            if guest_cart:
                session["cart"] = guest_cart
            if guest_wishlist:
                session["wishlist"] = guest_wishlist
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
    app.run()