from flask import session

def add_to_cart(product_id):
    cart = session.get("cart", {})
    product_id = str(product_id) #keys must be strings
    cart[product_id] = cart.get(product_id, 0) + 1
    session["cart"] = cart

def remove_from_cart(product_id):
    cart = session.get("cart", {})
    product_id = str(product_id)

    if product_id in cart:
        del cart[product_id]
    session["cart"] = cart

def update_quantity(product_id, quantity):
    cart = session.get("cart", {})
    product_id = str(product_id)
    if quantity > 0:
        cart[product_id] = quantity
    else:
        cart.pop(product_id, None)
    session["cart"] = cart