
from data.dummy_data import products

def get_product(product_id):
    """Fetch a single product by its ID from dummy data."""
    return next((p for p in products if p["id"] == product_id), None)
