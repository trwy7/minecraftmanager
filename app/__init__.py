import os
import functools
import importlib
import jwt
from flask import Flask, request, redirect
from flask_limiter import Limiter
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt

app = Flask(__name__, template_folder="pages", static_folder="static")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////data/db.sqlite3'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "ChangeM3P13ase")

db = SQLAlchemy(app)
migrate = Migrate(app, db)
limiter = Limiter(app=app, key_func=lambda: request.remote_addr, default_limits=["100/minute", "5/second"], storage_uri="memory://")
socketio = SocketIO(app)
bcrypt = Bcrypt(app)

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
        cusr = jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")['usr']
        usr = get_user(cusr)
        if usr:
            request.user = usr
    except jwt.exceptions.InvalidSignatureError:
        pass

def require_login(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if request.user:
            return func(*args, **kwargs)
        return redirect("/login")
    return wrapper

def require_no_login(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not request.user:
            return func(*args, **kwargs)
        return redirect("/dashboard")
    return wrapper

@app.route("/")
@require_login
def index():
    return redirect("/dashboard")

def check_password(phash: str, password: str):
    return bcrypt.check_password_hash(phash, password)

def get_user(uid):
    return User.query.filter_by(id=uid).first()

def get_user_count():
    return User.query.count()

def create_user(uid, password):
    user = User(id=uid, password=bcrypt.generate_password_hash(password).decode('utf-8'))
    db.session.add(user)
    db.session.commit()
    return user

class User(db.Model):
    id = db.Column(db.String(255), primary_key=True, unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    def generate_token(self):
        return jwt.encode({"usr": self.id}, app.config['SECRET_KEY'], algorithm="HS256")

class Server(db.Model):
    id = db.Column(db.String(255), primary_key=True, unique=True, nullable=False)
    name = db.Column(db.String(30), nullable=False)
    stop_cmd = db.Column(db.String(30), nullable=False)
    type = db.Column(db.String(5), nullable=False)

with app.app_context():
    db.create_all()

# Import routes
if os.environ.get("IN_DOCKER"):
    for root, _, files in os.walk("app/routes"):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                module_path = os.path.join(root, file).replace("/", ".").rstrip(".py")
                importlib.import_module(module_path)
