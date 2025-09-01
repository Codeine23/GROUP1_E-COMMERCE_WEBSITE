from flask import session
from data.dummy_data import products

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



def get_cart_items():
    cart_dict = session.get('cart', {})
    cart_items_with_details = []
    subtotal = 0

    for product_id, quantity in cart_dict.items():
        product = next((p for p in products if p['id'] == int(product_id)), None)
        if product:
            product_with_qty = product.copy()
            product_with_qty["quantity"] = quantity
            product_with_qty["subtotal"] = product["discount_price"] * quantity
            subtotal += product_with_qty["subtotal"]
            cart_items_with_details.append(product_with_qty)

    return cart_items_with_details, subtotal
