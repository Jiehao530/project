def product_scheme(data) -> dict:
    return {
        "id": str(data["_id"]),
        "name": data["name"],
        "price": data["price"],
        "quantity": data["quantity"],
        "category": data["category"]
    }