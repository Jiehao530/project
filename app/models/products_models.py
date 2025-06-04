from pydantic import BaseModel

class NewProduct(BaseModel):
    name: str
    price: float
    quantity: int
    category: str


class Product(BaseModel):
    id: str
    name: str
    price: float
    quantity: int
    category: str