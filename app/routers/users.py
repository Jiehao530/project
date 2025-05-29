from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from models.users_models import User, UserDataBase
from models.static_models import Roles, Status
from schemes.users_schemes import user_scheme, user_scheme_final
from services.client import client
from passlib.context import CryptContext
from datetime import datetime, timedelta
from bson import ObjectId

crypt = CryptContext(schemes=["bcrypt"])

router = APIRouter()

def search_user(field: str, value):
    try:
        search = client.users.find_one({field: value})
        search_dict = user_scheme(search)
        return UserDataBase(**search_dict)
    except:
        return None

@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup_user(data: User):
    if search_user("email", data.email) is not None:
        raise HTTPException(status_code=status.HTTP_302_FOUND, detail="This email is in use")
    if search_user("username", data.username) is not None:
        raise HTTPException(status_code=status.HTTP_302_FOUND, detail="This user is in use")
    
    data_dict = dict(data)
    data_dict["password"] = crypt.hash(data.password)
    data_dict["status"] = Status.ACTIVE
    data_dict["creation_date"] = datetime.utcnow()
    data_dict["last_login"] = datetime.utcnow()

    id = client.users.insert_one(data_dict).inserted_id
    new_user = search_user("_id", ObjectId(id))
    return user_scheme_final(dict(new_user))
