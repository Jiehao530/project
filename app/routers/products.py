import os
import sys
sys.path.insert(0, os.path.abspath(__file__) + "/../")
from fastapi import APIRouter, HTTPException, status, Depends
from services.client import client
from models.products_models import NewProduct, Product
from models.users_models import UserDataBase
from models.static_models import Roles
from users import get_user
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

@router.post("/products", status_code=status.HTTP_201_CREATED)
async def add_product(new_product: NewProduct, user: UserDataBase = Depends(get_user)):
    if user.rol != Roles.ADMIN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You don't have administrator permissions")
    if search_product("name", new_product.name) is not None:
        raise HTTPException(status_code=status.HTTP_302_FOUND, detail="The product is added")
    
    new_product_dict = dict(new_product)
    id_product = client.products.insert_one(new_product_dict).inserted_id
    search_new = search_product("_id", ObjectId(id_product))
    return search_new

@router.get("/products/{name}", status_code=status.HTTP_202_ACCEPTED)
async def get_product(name: str):
    product = search_product("name", name)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The product was not found")
    return product

