from flask import Flask
from config import Config
from models import db, bcrypt
from routes import routes
from flask_jwt_extended import JWTManager

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, Docker!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
