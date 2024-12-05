import os
import connect
import psycopg2
import bcrypt
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token

from config import load_config


REGISTER_USER = "INSERT INTO users (user_name, user_email, user_password) VALUES (%s, %s, %s) RETURNING user_id"
GET_USER_BY_EMAIL = "SELECT * FROM users WHERE user_email = %s"
load_dotenv()

app = Flask(__name__)
#Hashing key
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "your_jwt_secret_key")  # JWT Secret Key
jwt = JWTManager(app)

#database connection
url = os.getenv("DATABASE_URL")
config = load_config()
connection = psycopg2.connect(**config)

#endpoints in here for now, will later be moved 

@app.get("/")
def home():
    return "Hello, Docker!"

@app.post("/api/register")
def register_user():
    data = request.get_json()
    user_name = data["user_name"]
    user_email = data["user_email"]
    user_password = data["user_password"]

    hashed_password = bcrypt.hashpw(user_password.encode('utf8'), bcrypt.gensalt()).decode('utf-8')

    with connection:
        with connection.cursor() as cursor:
            cursor.execute(REGISTER_USER, (user_name, user_email, hashed_password))
            user_id = cursor.fetchone()[0]
    return {"id": user_id, "Message": f"User  {user_name} created."}, 201

@app.post("/api/login")
def login_user():
    data = request.get_json()
    user_email = data["user_email"]
    user_password = data["user_password"]
    
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(GET_USER_BY_EMAIL, (user_email,))
            user = cursor.fetchone()

    if not user:
        return jsonify({"error": "User not found"}), 404

    else:
        stored_password_hash = user[3]
        is_pass_matching = bcrypt.checkpw(user_password.encode('utf8'), stored_password_hash.encode('utf8'))

        if is_pass_matching:
            user_id = user[0]  
            access_token = create_access_token(identity=user_id)

            return jsonify({"token": access_token, "message": "Login successful"}), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 401
       

