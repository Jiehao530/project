import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)) + "/../")
from fastapi import APIRouter, HTTPException, status, Depends, Form
from models.products_models import NewProduct, Product, UpdateProduct
from models.users_models import UserDataBase
from models.static_models import Roles
from services.client import client
from routers.users import verify_token
from bson import ObjectId
from schemes.product_schemes import product_scheme, products_scheme

router = APIRouter()

def search_product(field: str, value):
    search = client.products.find_one({field: value})
    if search:
        return Product(**product_scheme(search))

def product_validation(name: str):
    product = search_product("name", name)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The product was not found")
    return product

def user_login_validation(user: UserDataBase):
    if not isinstance(user, UserDataBase):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You need to log in")

def user_admin_validation(user: UserDataBase):
    if user.rol != Roles.ADMIN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You don't have administrator permissions")

#FOR THE ADMINISTRATOR
@router.post("/products", status_code=status.HTTP_201_CREATED)
async def add_product(new_product: NewProduct, user: UserDataBase = Depends(verify_token)):
    user_login_validation(user)
    user_admin_validation(user)
    if search_product("name", new_product.name) is not None:
        raise HTTPException(status_code=status.HTTP_302_FOUND, detail="The product is added")
    
    new_product_dict = dict(new_product)
    id_product = client.products.insert_one(new_product_dict).inserted_id
    search_new = search_product("_id", ObjectId(id_product))
    return search_new

#FOR THE ADMINISTRATOR
@router.delete("/product/{name}", status_code=status.HTTP_200_OK)
async def delete_product(name: str, user: UserDataBase = Depends(verify_token)):
    user_login_validation(user)
    user_admin_validation(user)
    
    product = product_validation(name)
    delete = client.products.find_one_and_delete({"_id": ObjectId(product.id)})
    if delete is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The product could not be deleted")
    return {"detail": f"The product {product.name} has been successfully deleted"}


#FOR THE CLIENT AND ADMINISTRATOR
@router.get("/product/{name}", status_code=status.HTTP_202_ACCEPTED)
async def get_product(name: str):
    product = search_product("name",name)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The product was not found")
    return product

#FOR THE CLIENT
@router.get("/products", status_code=status.HTTP_202_ACCEPTED)
async def get_products():
    products_list = client.products.find()
    return products_scheme(products_list)

#FOR THE ADMINISTRATOR
@router.patch("/product/{name}", status_code=status.HTTP_202_ACCEPTED)
async def update_product(name: str, product_new_data: UpdateProduct, user: UserDataBase = Depends(verify_token), product: Product = Depends(get_product)):
    user_login_validation(user)
    user_admin_validation(user)
    product_validation(name)

    product_new_data_dict = product_new_data.dict(exclude_unset=True)
    print(product_new_data_dict)
    if "name" in product_new_data_dict:
        product_name_existing = client.products.find_one({"name": product_new_data_dict["name"], "_id": {"$ne": ObjectId(product.id)}})
        if product_name_existing is not None:
            raise HTTPException(status_code=status.HTTP_302_FOUND, detail="The product exists")

    update = client.products.update_one({"_id": ObjectId(product.id)}, {"$set": product_new_data_dict})
    if update.modified_count == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The product has not been updated")
    return search_product("_id", ObjectId(product.id))
    
#FOR THE CLIENT
@router.post("/product/{name}/buy", status_code=status.HTTP_202_ACCEPTED)
async def buy_product(name: str, quantity: int = Form(...), user: UserDataBase = Depends(verify_token)):
    if not isinstance(user, UserDataBase):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You need to log in to purchase")
    product = product_validation(name)

    if product.quantity == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Out of stock")
    if product.quantity < quantity:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not enough stock available")
    
    purchased = product.quantity - quantity

    update = client.products.update_one({"_id": ObjectId(product.id)}, {"$set": {"quantity": purchased}})
    if update.modified_count == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not be updated")
    return {"detail": f"Purchased {quantity} units of {product.name}"}
