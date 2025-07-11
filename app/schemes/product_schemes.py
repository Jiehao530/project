def product_scheme(data) -> dict:
    return {
        "id": str(data["_id"]),
        "name": data["name"],
        "description": data["description"],
        "price": data["price"],
        "quantity": data["quantity"],
        "category": data["category"]
    }

def products_scheme(data) -> list:
    return [product_scheme(product) for product in data]