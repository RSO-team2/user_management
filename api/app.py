import os
import psycopg2
import bcrypt
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from prometheus_flask_exporter import PrometheusMetrics


REGISTER_USER = "INSERT INTO users (user_name, user_email, user_password, user_address, user_type) VALUES (%s, %s, %s, %s, %s) RETURNING user_id"
GET_USER_BY_EMAIL = "SELECT * FROM users WHERE user_email = %s"
GET_USER_BY_ID = "SELECT * FROM users WHERE user_id = %s"
GET_USERT_TYPE_ID = "SELECT id FROM user_types WHERE type = %s"
load_dotenv()

app = Flask(__name__)
cors = CORS(app)

metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Restaurant Management API Info', version='1.0.0')

def check_database_connection():
    """
    Checks if the database connection is active and operational.
    Raises an exception if the database is not reachable.
    """
    try:
        # Connect to your PostgreSQL database
        connection = psycopg2.connect(os.getenv("DATABASE_URL"))
        cursor = connection.cursor()
        cursor.execute(
            "SELECT 1"
        )  # Simple query to check if the database is responsive
        connection.close()
        print("Database is connected!")
    except OperationalError as err:
        raise Exception("Database is not reachable: " + str(err))


@app.route("/health")
def health_check():
    """
    Health check endpoint to verify the service's status.
    Returns:
        - "Service is healthy" with a 200 status if the database connection is operational.
        - "Service is unhealthy" with a 500 status if the connection check fails.
    """
    try:
        check_database_connection()
        return "Service is healthy", 200
    except:
        return "Service is unhealthy", 500


@app.post("/api/register")
@cross_origin()
def register_user():
    """
    Registers a new user in the system.
    Validates input, hashes the user's password, and inserts the new user into the database.
    Returns:
        - Success: JSON object with the user's ID, type, and success message (status 201).
        - Failure: JSON object with an error message if the email already exists or user type is invalid.
    """
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
    return (
        jsonify(
            {
                "user_id": user_id,
                "user_type": user_type,
                "Message": f"User  {user_name} created.",
            }
        ),
        201,
    )


@app.post("/api/link_restaurant")
@cross_origin()
def link_restaurant():
    """
    Links a restaurant to a user by updating the user's record in the database.
    Returns:
        - Success: JSON object with a success message (status 200).
    """
    data = request.get_json()
    user_id = data["user_id"]
    restaurant_id = data["restaurant_id"]

    connection = psycopg2.connect(os.getenv("DATABASE_URL"))
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE users SET restaurant_id = %s WHERE user_id = %s",
                (restaurant_id, user_id),
            )

    return jsonify({"message": "Restaurant linked to user"}), 200


@app.post("/api/login")
@cross_origin()
def login_user():
    """
    Authenticates a user by validating their email and password.
    Returns:
        - Success: JSON object with a success message, user ID, and user type (status 200).
        - Failure: JSON object with an error message if the user is not found or credentials are invalid.
    """
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
            return (
                jsonify(
                    {
                        "message": "Login successful",
                        "user_id": user[0],
                        "user_type": user[5],
                    }
                ),
                200,
            )
        else:
            return jsonify({"error": "Invalid credentials"}), 401


@app.get("/api/getUserInfo")
@cross_origin()
def get_user_info():
    """
    Retrieves information about a specific user based on their user ID.
    Returns:
        - Success: JSON object with user details such as name, email, address, type, and linked restaurant (status 200).
        - Failure: JSON object with an error message if the user is not found (status 404).
    """
    user_id = request.args.get("user_id")

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
        user_type = user[5]
        restaurant_id = user[6]
        return jsonify(
            {
                "user_name": user_name,
                "user_email": user_email,
                "adress": user_address,
                "user_type": user_type,
                "restaurant_id": restaurant_id,
            }
        )


if __name__ == "__main__":
    print("Starting app...")
    app.run(host="0.0.0.0", port=5000)
