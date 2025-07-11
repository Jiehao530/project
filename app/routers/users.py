import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/../"))
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from models.users_models import User, UserDataBase
from models.static_models import Roles, Status
from schemes.users_schemes import user_scheme, user_scheme_final, user_admin_scheme
from services.client import client
from passlib.context import CryptContext
from datetime import datetime, timedelta
from bson import ObjectId
from jose import jwt, JWTError

ALGORITHM = "HS256"
ACCESS_TOKEN_DURATION = timedelta(hours=6)
SECRET = "e3f1a8b7c9d6e4f2a1b0c3d5e7f8a9b6c4d2e0f1a3b5c7d9e6f4a2b0c1d3e5f7"
crypt = CryptContext(schemes=["bcrypt"])

router = APIRouter()
oauth2 = OAuth2PasswordBearer(tokenUrl="/login")

def search_user(field: str, value):
    search = client.users.find_one({field: value})
    if search:
        return UserDataBase(**user_scheme(search))


def get_token(user: UserDataBase):
    data_token = {
        "sub": user.username,
        "exp": datetime.utcnow() + ACCESS_TOKEN_DURATION
    }
    token = jwt.encode(data_token, SECRET, algorithm=ALGORITHM)

    client.tokens.insert_one({
        "user_id": ObjectId(user.id),
        "username": user.username,
        "token": token,
        "created_at": datetime.utcnow()
    })
    return token

async def verify_token(token: str = Depends(oauth2)):
    try: 
        data_token = jwt.decode(token, SECRET, algorithms=ALGORITHM, options={"verify_exp":False})

        expire = data_token.get("exp")
        if expire is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect token")
        if datetime.utcfromtimestamp(expire) < datetime.utcnow():
            client.tokens.delete_one({"token": token})
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired, please log in again")
        
        username = data_token.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect token")
        user = search_user("username", username)
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect token")
        if user.status == Status.INACTIVE:
            raise HTTPException(status_code=status.HTTP_423_LOCKED, detail="This user is inactive")
        return user
    
    except JWTError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect token")

def user_validation(username: str):
    user = search_user("username", username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This user doesn't exist")
    return user

def id_validation(id_user: str, id_data: str):
    if id_user != id_data: 
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You don't have permission to access this user")

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

@router.post("/login", status_code=status.HTTP_200_OK)
async def login_user(form: OAuth2PasswordRequestForm = Depends()):
    user = search_user("username", form.username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This user doesn't exist")
    if not crypt.verify(form.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")
    
    existing_token = client.tokens.find_one({"user_id": ObjectId(user.id)})
    if existing_token:
        client.tokens.delete_one({"user_id": ObjectId(user.id)})
    
    token = get_token(user)
    return {"Token": token, "Token_type": "Bearer"}

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout_user(user: UserDataBase = Depends(verify_token)):
    logout = client.tokens.delete_one({"user_id": ObjectId(user.id)})
    if logout.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not log out")

    return {"detail": "User successfully logged out"}

@router.get("/user/{username}", status_code=status.HTTP_202_ACCEPTED)
async def get_user(username: str, data: UserDataBase = Depends(verify_token)):
    validation = user_validation(username)
    id_validation(validation.id, data.id)

    user = user_scheme_final(dict(data))
    return UserDataBase(**user)

@router.get("/user/{username}/admin", status_code=status.HTTP_202_ACCEPTED)
async def get_user_admin(username: str, data: UserDataBase = Depends(verify_token)):
    validation = user_validation(username)
    id_validation(validation.id, data.id)
    if validation.rol != Roles.ADMIN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You don't have administrator permissions")
    
    usersdatabase = client.users.find()
    return user_admin_scheme(usersdatabase)

@router.delete("/user/{username}/admin/{username_delete}", status_code=status.HTTP_202_ACCEPTED)
async def delete_user_by_admin(username: str, username_delete: str, data: UserDataBase = Depends(get_user)):
    validation = user_validation(username)
    id_validation(validation.id, data.id)
    if validation.rol != Roles.ADMIN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You don't have administrator permissions")
    
    user_delete_validation = user_validation(username_delete)
    existing_token = client.tokens.find_one({"user_id": ObjectId(user_delete_validation.id)})
    if existing_token:
        client.tokens.delete_one({"user_id": ObjectId(user_delete_validation.id)})
    
    user_delete = client.users.find_one_and_delete({"_id": ObjectId(user_delete_validation.id)})
    if user_delete is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The user could not be deleted")
    return {"detail": f"The user {username_delete} has been successfully deleted"}

@router.patch("/user/{username}", status_code=status.HTTP_202_ACCEPTED)
async def update_user(username: str, new_data: User, data: UserDataBase = Depends(get_user)):
    validation = user_validation(username)
    id_validation(validation.id, data.id)
    
    existing_email = client.users.find_one({"email": new_data.email, "_id": {"$ne": ObjectId(data.id)}})
    if existing_email is not None:
        raise HTTPException(status_code=status.HTTP_302_FOUND, detail="This email is in use")
    existing_username = client.users.find_one({"username": new_data.username, "_id": {"$ne": ObjectId(data.id)}})
    if existing_username is not None:
        raise HTTPException(status_code=status.HTTP_302_FOUND, detail="This username is in use")
    
    new_data_dict = dict(new_data)
    if crypt.verify(new_data.password, search_user("_id", ObjectId(data.id)).password):
        del new_data_dict["password"]
    else:
        new_data_dict["password"] = crypt.hash(new_data.password)
    
    update = client.users.update_one({"_id": ObjectId(data.id)},{"$set": new_data_dict})
    if update.modified_count == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not be updated")
    get_update = search_user("_id", ObjectId(data.id))
    return user_scheme_final(dict(get_update))

@router.delete("/user/{username}", status_code=status.HTTP_200_OK)
async def delete_user(username: str, data: UserDataBase = Depends(get_user)):
    validation = user_validation(username)
    id_validation(validation.id, data.id)

    existing_token = client.tokens.find_one({"user_id": ObjectId(data.id)})
    if existing_token:
        client.tokens.delete_one({"user_id": ObjectId(data.id)})

    delete = client.users.find_one_and_delete({"_id": ObjectId(data.id)})
    if delete is None: 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The user could not be deleted")
    return {"detail": "The user has been successfully deleted"}