from fastapi import FastAPI
from routers import users, products

#uvicorn main:app --reload
app = FastAPI()
app.include_router(users.router)
app.include_router(products.router)


@app.get("/")
async def root():
    return "Welcome to my project"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
