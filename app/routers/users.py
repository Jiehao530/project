from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from models.users_models import User, UserDataBase
from models.static_models import Roles, Status
from schemes.users_schemes import user_scheme, user_scheme_final
from services.client import client
from passlib.context import CryptContext
from datetime import datetime, timedelta
from bson import ObjectId
from jose import jwt, JWTError

ALGORITHM = "HS256"
ACCESS_TOKEN_DURATION = timedelta(hours=1)
SECRET = "e3f1a8b7c9d6e4f2a1b0c3d5e7f8a9b6c4d2e0f1a3b5c7d9e6f4a2b0c1d3e5f7"
crypt = CryptContext(schemes=["bcrypt"])

router = APIRouter()
outh2 = OAuth2PasswordBearer(tokenUrl="/login")

def search_user(field: str, value):
    try:
        search = client.users.find_one({field: value})
        search_dict = user_scheme(search)
        return UserDataBase(**search_dict)
    except:
        return None

def get_token(user: str):
    data_token = {
        "sub": user,
        "exp": datetime.utcnow + ACCESS_TOKEN_DURATION
    }
    token = jwt.encode(data_token, SECRET, algorithm=ALGORITHM)
    return token

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

@router.post("/login")
async def login_user(form: OAuth2PasswordRequestForm = Depends()):
    user = search_user("username", form.username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This user doesn't exist")
    if not crypt.verify(form.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")
    
    token = get_token(user.username)
    return {"Token": token, "Token_type": "Bearer"}
    