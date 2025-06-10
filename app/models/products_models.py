import os 
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)) + "/../")
from models.static_models import Category
from typing import Optional
from pydantic import BaseModel

class NewProduct(BaseModel):
    name: str
    description: str
    price: float
    quantity: int
    category: Category


class Product(BaseModel):
    id: str
    name: str
    description: str
    price: float
    quantity: int
    category: Category

class UpdateProduct(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = None
    category: Optional[Category] = None