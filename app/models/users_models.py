from pydantic import BaseModel, constr, EmailStr
from static_models import Roles, Status
from datetime import datetime

class User(BaseModel):
    username: constr(min_length=6, max_length=18, pattern=r"^[a-zA-Z0-9._-]$")
    password: constr(min_length=8, max_length=20, pattern=r"^[a-zA-Z0-9._-@%*+/]$")
    email: EmailStr
    department: str
    rol: Roles

class UserDataBase(User):
    id: str
    status: Status
    creation_date: datetime
    last_login: datetime