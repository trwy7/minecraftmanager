import jwt
import os
from flask import Flask, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////data/db.sqlite3'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "ChangeM3P13ase")

db = SQLAlchemy(app)
migrate = Migrate(app, db)

@app.before_request
def verify_user():
    auth = request.headers.get("Authorization")
    # Check cookies, query string and URL parameters for an auth token
    token = request.cookies.get("token")
    if auth and auth.startswith("Bearer "):
        token = auth.split(" ")[1]
    request.user = None
    try:
        jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")
    except jwt.exceptions.InvalidSignatureError:
        pass

def require_login(func):
    def wrapper():
        if request.user:
            return func()
        return redirect("/login")
    return wrapper

class User(db.Model):
    id = db.Column(db.String(255), primary_key=True, unique=True, nullable=False)
    def generate_token(self):
        jwt.encode({"usr": self.id}, app.config['SECRET_KEY'], algorithm="HS256")

class Server(db.Model):
    id = db.Column(db.String(255), primary_key=True, unique=True, nullable=False)
    name = db.Column(db.String(30), nullable=False)
    stop_cmd = db.Column(db.String(30), nullable=False)
    type = db.Column(db.String(5), nullable=False)
