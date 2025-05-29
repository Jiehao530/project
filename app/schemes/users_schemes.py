def user_scheme(data) -> dict:
    return{
        "id": str(data["_id"]),
        "username": data["username"],
        "password": data["password"],
        "email": data["email"],
        "department": data["department"],
        "rol": data["rol"],
        "status": data["status"],
        "creation_date": data["creation_date"],
        "last_login": data["last_login"]
    }

def user_scheme_final(data) -> dict:
    return{
        "id": data["id"],
        "username": data["username"],
        "password": "*******",
        "email": data["email"],
        "department": data["department"],
        "rol": data["rol"],
        "status": data["status"],
        "creation_date": data["creation_date"],
        "last_login": data["last_login"]
    }
def user_admin_scheme(list_users) -> list:
    return [user_scheme(user) for user in list_users]