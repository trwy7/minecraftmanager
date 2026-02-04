import os
import importlib
import jwt
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
    if not token:
        token = request.args.get("token")
    if not token:
        return
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

def require_no_login(func):
    def wrapper():
        if not request.user:
            return func()
        return redirect("/dashboard")
    return wrapper

@app.route("/")
@require_login
def index():
    return redirect("/dashboard")

class User(db.Model):
    id = db.Column(db.String(255), primary_key=True, unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    def generate_token(self):
        return jwt.encode({"usr": self.id}, app.config['SECRET_KEY'], algorithm="HS256")
    def get_user(self, uid):
        return User.query.filter_by(id=uid).first()

class Server(db.Model):
    id = db.Column(db.String(255), primary_key=True, unique=True, nullable=False)
    name = db.Column(db.String(30), nullable=False)
    stop_cmd = db.Column(db.String(30), nullable=False)
    type = db.Column(db.String(5), nullable=False)

# Import routes
if os.environ.get("IN_DOCKER"):
    for root, _, files in os.walk("app/routes"):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                module_path = os.path.join(root, file).replace("/", ".").rstrip(".py")
                importlib.import_module(module_path)
