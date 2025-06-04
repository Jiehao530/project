import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)) + "/../")
from fastapi import APIRouter, HTTPException, status, Depends, Form
from models.products_models import NewProduct, Product
from models.users_models import UserDataBase
from models.static_models import Roles
from services.client import client
from routers.users import get_user, verify_token
from bson import ObjectId
from schemes.product_schemes import product_scheme

router = APIRouter()

def search_product(field: str, value):
    try:
        search = client.products.find_one({field: value})
        search_dict = product_scheme(search)
        return Product(**search_dict)
    except:
        return None

def product_validation(name: str):
    product = search_product("name", name)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The product was not found")
    return product

@router.post("/products", status_code=status.HTTP_201_CREATED)
async def add_product(new_product: NewProduct, user: UserDataBase = Depends(verify_token)):
    if not isinstance(user, UserDataBase):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You need to log in")
    if user.rol != Roles.ADMIN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You don't have administrator permissions")
    if search_product("name", new_product.name) is not None:
        raise HTTPException(status_code=status.HTTP_302_FOUND, detail="The product is added")
    
    new_product_dict = dict(new_product)
    id_product = client.products.insert_one(new_product_dict).inserted_id
    search_new = search_product("_id", ObjectId(id_product))
    return search_new

@router.get("/product/{name}", status_code=status.HTTP_202_ACCEPTED)
async def get_product(name: str):
    product = search_product("name", name)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The product was not found")
    return product

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
