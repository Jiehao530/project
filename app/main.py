from fastapi import FastAPI
from routers import users

#uvicorn main:app --reload
app = FastAPI()
app.include_router(users.router)

