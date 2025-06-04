from pydantic import BaseModel

class NewProduct(BaseModel):
    name: str
    description: str
    price: float
    quantity: int
    category: str


class Product(BaseModel):
    id: str
    name: str
    description: str
    price: float
    quantity: int
    category: str