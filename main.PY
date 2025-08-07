          

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import mysql.connector
from fastapi.responses import JSONResponse
import base64

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="prajesh@1",
    database="AGROKART"
)
cursor = db.cursor()

# ================== LOGIN ENDPOINT ===================
class LoginRequest(BaseModel):
    email: str
    password: str

@app.post("/login")
def login(request: LoginRequest):
    query = "SELECT * FROM users WHERE email=%s AND password=%s"
    cursor.execute(query, (request.email, request.password))
    result = cursor.fetchone()

    if result:
        return {"message": "Login successful"}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    




from pydantic import BaseModel
from fastapi import HTTPException
import re

# Pydantic model for sign up request
class SignUpRequest(BaseModel):
    full_name: str
    email: str
    phone: str
    password: str

@app.post("/signup")
def signup(request: SignUpRequest):
    # Basic validation
    if len(request.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters long")
    
    # Email validation (basic)
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, request.email):
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    # Phone validation (basic - adjust pattern as needed)
    phone_pattern = r'^[\+]?[1-9][\d]{0,15}$'
    if not re.match(phone_pattern, request.phone.replace(" ", "").replace("-", "")):
        raise HTTPException(status_code=400, detail="Invalid phone number format")
    
    # Check if user already exists
    check_query = "SELECT * FROM users WHERE email=%s"
    cursor.execute(check_query, (request.email,))
    existing_user = cursor.fetchone()
    
    if existing_user:
        raise HTTPException(status_code=409, detail="User with this email already exists")
    
    try:
        # Insert new user into database
        insert_query = "INSERT INTO users (full_name, email, phone, password) VALUES (%s, %s, %s, %s)"
        cursor.execute(insert_query, (request.full_name, request.email, request.phone, request.password))
        
        # Commit the transaction
        db.commit()
        
        return {"message": "User registered successfully"}
        
    except Exception as e:
        # Rollback in case of error
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create user")

# ================== REGISTER ENDPOINT ===================
class RegisterRequest(BaseModel):
    email: str
    password: str

@app.post("/register")
def register(request: RegisterRequest):
    # Check if user already exists
    cursor.execute("SELECT * FROM users WHERE email = %s", (request.email,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="User already exists")

    # Insert new user
    cursor.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (request.email, request.password))
    db.commit()
    return {"message": "Registration successful"}

# =========== Add Product ===========
@app.post("/add-product")
async def add_product(
    productName: str = Form(...),
    productQuantity: str = Form(...),
    productImage: UploadFile = File(...)
):
    image_bytes = await productImage.read()
    query = "INSERT INTO products (name, quantity, image) VALUES (%s, %s, %s)"
    cursor.execute(query, (productName, productQuantity, image_bytes))
    db.commit()
    return {"message": "Product added successfully"}

# =========== Get All Products ===========
@app.get("/get-products")
def get_products():
    cursor.execute("SELECT id, name, quantity, image FROM products")
    products = cursor.fetchall()
    result = []
    for id, name, quantity, image in products:
        image_base64 = base64.b64encode(image).decode("utf-8")
        result.append({
            "id": id,
            "name": name,
            "quantity": quantity,
            "image": image_base64
        })
    return JSONResponse(content=result)

# =========== Add to Cart ===========
class CartItem(BaseModel):
    product_id: int

@app.post("/add-to-cart")
def add_to_cart(item: CartItem):
    cursor.execute("INSERT INTO cart (product_id) VALUES (%s)", (item.product_id,))
    db.commit()
    return {"message": "Product added to cart"}

# =========== Get Cart Items ===========
@app.get("/get-cart")
def get_cart():
    cursor.execute("""
        SELECT p.id, p.name, p.quantity, p.image
        FROM cart c
        JOIN products p ON c.product_id = p.id
    """)
    items = cursor.fetchall()
    cart_items = []
    for id, name, quantity, image in items:
        image_base64 = base64.b64encode(image).decode("utf-8")
        cart_items.append({
            "id": id,
            "name": name,
            "quantity": quantity,
            "image": image_base64
        })
    return JSONResponse(content=cart_items)

# =========== Clear Cart ===========
@app.delete("/clear-cart")
def clear_cart():
    cursor.execute("DELETE FROM cart")
    db.commit()
    return {"message": "Cart cleared"}