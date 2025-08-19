from flask import Flask, render_template
import sqlite3

app = Flask(__name__)


@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/cart")
def cart():
    return render_template("cart.html")

@app.route("/contact_us")
def contact():
    return render_template("contact_us.html")

@app.route("/gadgets")
def gadget():
    return render_template("gadgets.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/last30days")
def last_days():
    return render_template("last30days.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/shoes")
def shoes():
    return render_template("shoes.html")

@app.route("/wishlist")
def wishlist():
    return render_template("wishlist.html")

@app.route("/men_clothings")
def men():
    return render_template("mn_clthn.html")

@app.route("/women_clothings")
def women():
    return render_template("wm_clthn.html")

@app.route("/admin/admin_login")
def admin_login():
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