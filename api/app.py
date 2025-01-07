import os
import psycopg2
import bcrypt
import asyncio
from nats.aio.client import Client as NATS
from threading import Thread
from dotenv import load_dotenv
from flask import Flask, request, jsonify


REGISTER_USER = "INSERT INTO users (user_name, user_email, user_password, user_address, user_type) VALUES (%s, %s, %s, %s, %s) RETURNING user_id"
GET_USER_BY_EMAIL = "SELECT * FROM users WHERE user_email = %s"
GET_USER_BY_ID = "SELECT * FROM users WHERE user_id = %d"
GET_USERT_TYPE_ID = "SELECT id FROM user_types WHERE type = %s"
load_dotenv()

app = Flask(__name__)

async def handle_message(msg):
    data = msg.data.decode('utf-8')
    print(f"Received a new reservation")


async def run_nats_subscription():
    nc = NATS()
    await nc.connect(servers=[" nats://nats.default.svc.cluster.local:4222"])
    await nc.subscribe("reservation.created", cb=handle_message)

    print("Listening for messages on 'reservation.created'...")
    while True:
        await asyncio.sleep(1)  # Keep the event loop running

@app.post("/api/register")
def register_user():
    data = request.get_json()
    user_name = data["user_name"]
    user_email = data["user_email"]
    user_password = data["user_password"]
    user_address = data["user_address"]
    user_type = data["user_type"]

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
            
            cursor.execute(GET_USERT_TYPE_ID, (user_type,))
            user_type = cursor.fetchone()[0]
            if not user_type:
                return {"error": "Invalid user type"}, 400

            cursor.execute(
                REGISTER_USER,
                (user_name, user_email, hashed_password, user_address, user_type),
            )
            user_id = cursor.fetchone()[0]
    return jsonify({"user_id": user_id, "Message": f"User  {user_name} created."}), 201


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
            return jsonify({"message": "Login successful", "user_id": user[0]}), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 401


@app.post("/api/getUserInfo")
def get_user_info():
    data = request.get_json()
    user_id = data["user_id"]

    connection = psycopg2.connect(os.getenv("DATABASE_URL"))

    with connection:
        with connection.cursor() as cursor:
            cursor.execute(GET_USER_BY_ID, (user_id,))
            user = cursor.fetchone()

    if not user:
        return jsonify({"error": "User not found"}), 404

    else:
        user_name = user[1]
        user_email = user[2]
        user_address = user[4]
        return jsonify(
            {"user_name": user_name, "user_email": user_email, "adress": user_address}
        )


if __name__ == "__main__":



    def start_flask():
        print("Starting Flask app...")
        app.run(host="0.0.0.0", port=5001, use_reloader=False, debug=False)

    async def main():
        # Run the NATS subscription in an asyncio task
        await run_nats_subscription()

    # Start Flask in a separate thread
    flask_thread = Thread(target=start_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Run NATS subscription asynchronously
    asyncio.run(main())
