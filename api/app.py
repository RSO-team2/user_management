import os
import psycopg2
import bcrypt
from dotenv import load_dotenv
from flask import Flask, request, jsonify


REGISTER_USER = "INSERT INTO users (user_name, user_email, user_password, user_adress) VALUES (%s, %s, %s, %s) RETURNING user_id"
GET_USER_BY_EMAIL = "SELECT * FROM users WHERE user_email = %s"
load_dotenv()

app = Flask(__name__)


@app.post("/api/register")
def register_user():
    data = request.get_json()
    user_name = data["user_name"]
    user_email = data["user_email"]
    user_password = data["user_password"]
    user_adress = data["user_adress"]

    hashed_password = bcrypt.hashpw(
        user_password.encode("utf8"), bcrypt.gensalt()
    ).decode("utf-8")

    connection = psycopg2.connect(os.getenv("DATABASE_URL"))
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(GET_USER_BY_EMAIL, (user_email,))
            email_exists = cursor.fetchone()

            if email_exists:
                return {
                    "error": "Email already exists. Please use a different email."
                }, 400

            cursor.execute(
                REGISTER_USER, (user_name, user_email, hashed_password, user_adress)
            )
            user_id = cursor.fetchone()[0]
    return {"id": user_id, "Message": f"User  {user_name} created."}, 201


@app.post("/api/login")
def login_user():
    data = request.get_json()
    user_email = data["user_email"]
    user_password = data["user_password"]

    connection = psycopg2.connect(os.getenv("DATABASE_URL"))

    with connection:
        with connection.cursor() as cursor:
            cursor.execute(GET_USER_BY_EMAIL, (user_email,))
            user = cursor.fetchone()

    if not user:
        return jsonify({"error": "User not found"}), 404

    else:
        stored_password_hash = user[3]
        is_pass_matching = bcrypt.checkpw(
            user_password.encode("utf8"), stored_password_hash.encode("utf8")
        )

        if is_pass_matching:
            user_id = user[0]
            # access_token = create_access_token(identity=user_id)

            return jsonify({"message": "Login successful"}), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 401


@app.post("/api/getUserInfo")
def get_user_info():
    data = request.get_json()
    user_email = data["user_email"]

    connection = psycopg2.connect(os.getenv("DATABASE_URL"))

    with connection:
        with connection.cursor() as cursor:
            cursor.execute(GET_USER_BY_EMAIL, (user_email,))
            user = cursor.fetchone()

    if not user:
        return jsonify({"error": "User not found"}), 404

    else:
        user_name = user[1]
        user_adress = user[4]
        return jsonify({"user_name": user_name, "adress": user_adress})


if __name__ == "__main__":
    print("Starting app...")
    app.run(host="0.0.0.0", port=5001)
