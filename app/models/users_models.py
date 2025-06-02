import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/../"))
from pydantic import BaseModel, constr, EmailStr
from models.static_models import Roles, Status
from datetime import datetime

class User(BaseModel):
    username: constr(pattern=r"^[a-zA-Z0-9._-]{6,18}$")
    password: constr(pattern=r"^[a-zA-Z0-9._\-@%*+/]{8,20}$")
    email: EmailStr
    department: str
    rol: Roles

class UserDataBase(BaseModel):
    username: str
    password: str
    email: EmailStr
    department: str
    rol: Roles
    id: str
    status: Status
    creation_date: datetime
    last_login: datetime