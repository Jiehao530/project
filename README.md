
# BACKEND API FOR USER AND PRODUCT MANAGEMENT

## DESCRIPTION

REST API with FastAPI and MongoDB that offers JWT authentication, role control, and a CRUD product system with purchasing and inventory management capabilities.

## TECHNOLOGIES USED

- FastAPI - Framework  
- MongoDB - NoSQL Database
- PyMongo - Connector for MongoDB
- passlib - Secure Password Hashing
- python-jose - JWT Token Management

## INSTALLING
```bash
git clone git@github.com:Jiehao530/project.git
```
```bash
pip install -r requirements.txt
```
## RUN THE PROJECT'S SOURCE CODE

```bash
python main.py
```
OR
```bash
uvicorn main:app --reload
```

## MAIN ENDPOINTS

__Authentication and Users__

- POST /signup: Register a new user

- POST /login: Get a JWT token

- GET /user/{username}: Get authenticated user data

- PATCH /user/{username}: Edit the user's profile

- DELETE /user/{username}: Delete your own account

- GET /user/{username}/admin: (admin) Get all users

- DELETE /user/{username}/admin/{username_delete}: (admin) Delete a specific user

__Products__

- POST /products: (admin) Create a new product

- PATCH /product/{name}: (admin) Update a product

- DELETE /product/{name}: (admin) Delete a product

- GET /products: List all products

- GET /product/{name}: View product details

- POST /product/{name}/buy: Buy a product (user) authenticated)

## AUTHOR

- [Jiehao530](https://github.com/Jiehao530)

