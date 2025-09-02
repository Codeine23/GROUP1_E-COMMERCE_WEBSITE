from flask import session
from data.dummy_data import products

def add_to_wishlist_helper(product_id):
    wishlist = session.get("wishlist", set())
    # Flask sessions don’t support sets directly, so we use a list
    wishlist = set(wishlist)  
    wishlist.add(str(product_id))
    session["wishlist"] = list(wishlist)


def remove_from_wishlist_helper(product_id):
    wishlist = session.get("wishlist", set())
    wishlist = set(wishlist)
    wishlist.discard(str(product_id))
    session["wishlist"] = list(wishlist)


def get_wishlist_items():
    wishlist_ids = session.get("wishlist", [])
    wishlist_items = []

    for product_id in wishlist_ids:
        product = next((p for p in products if p['id'] == int(product_id)), None)
        if product:
            wishlist_items.append(product)

    return wishlist_items
