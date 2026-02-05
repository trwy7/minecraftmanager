import os
import sys
import functools
import importlib
import shutil
import threading
import subprocess
import time
import signal
import jwt
from flask import Flask, request, redirect
from flask_limiter import Limiter
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from rcon.source import Client
from rcon.exceptions import EmptyResponse

print("Importing routes...")
app = Flask(__name__, template_folder="pages", static_folder="static")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////data/db.sqlite3'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "ChangeM3P13ase")

print("init db")
db = SQLAlchemy(app)
print("init limiter")
limiter = Limiter(app=app, key_func=lambda: request.remote_addr, default_limits=["100/minute", "5/second"], storage_uri="memory://")
#print("init socketio")
#socketio = SocketIO(app)
print("init bcrypt")
bcrypt = Bcrypt(app)

print("This app requires that you agree to the Minecraft EULA. If you do not, please remove the app and related files.")
print("You may view it here: https://aka.ms/MinecraftEULA")

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

# AI disclosure
# AI and a lot of manual debugging ahead

# In-memory mapping for server runtime state (proc/thread) keyed by server id.
# Use this so different SQLAlchemy model instances can reference the same runtime state.
server_states = {}

def is_server_running(server):
    """Return True if the server's process is currently running."""
    sid = server.id
    proc = server_states.get(sid, {}).get("proc")
    return proc is not None and proc.poll() is None

def run_server(server):
    """Run the given server and stream its stdout to the server's output.log."""
    sid = server.id
    cmd = f"/servers/{sid}/run.sh"
    cwd = f"/servers/{sid}"
    # Run without a shell to ensure stdout is captured correctly
    with subprocess.Popen(
        [cmd],
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=False
    ) as proc:
        # store the proc in the shared server state
        server_states.setdefault(sid, {})["proc"] = proc
        log_path = f"{cwd}/output.log"
        with open(log_path, "wb") as f:
            for line in iter(proc.stdout.readline, b""):
                #print(f"[{server.name}] {line.decode()}", end="")
                #socketio.emit("server_output", {"server_id": server.id, "output": line.decode()})
                f.write(line)
                f.flush()
            f.write(b"[mcm] Server process ended.\n")
        proc.wait()
        # clear the proc when finished
        server_states.setdefault(sid, {})["proc"] = None

def start_server(server):
    """Start the server in a background thread if not already running."""
    print(f"Starting server {server.name}...")
    sid = server.id
    thread = server_states.get(sid, {}).get("thread")
    if thread and thread.is_alive():
        return True
    thread = threading.Thread(target=run_server, daemon=True, args=(server,))
    server_states.setdefault(sid, {})["thread"] = thread
    thread.start()
    return thread

def run_command(server, command):
    """Run an RCON command on the server and return its response."""
    print(f"Running command '{command}' on server '{server.name}'...")
    if not is_server_running(server):
        print(f"Server {server.name} is not running, cannot run command '{command}'")
        return None
    with Client('127.0.0.1', server.id + 1000, passwd='mcmanager') as client:
        try:
            response = client.run(*command.split(" "))
        except EmptyResponse:
            response = None
        except ConnectionRefusedError:
            print(f"Failed to connect to server {server.name} for command '{command}'. RCON is likely not initialized yet.")
            return None
    print(f"Ran command '{command}' on server '{server.name}' with response: {response}")
    return response

def stop_server(server):
    """Stop the server gracefully, killing it if necessary."""
    sid = server.id
    proc = server_states.get(sid, {}).get("proc")
    print(f"Stopping server {server.name} with status {proc}...")
    if not is_server_running(server):
        print(f"Server {server.name} is not running.")
        return None
    print(f"Sending stop command to server {server.name}...")
    run_command(server, server.stop_cmd)
    if proc:
        try:
            proc.wait(timeout=60)
        except Exception:
            pass
    thread = server_states.get(sid, {}).get("thread")
    if thread and thread.is_alive():
        print(f"Server {server.name} did not stop gracefully, killing process...")
        if proc:
            proc.kill()
    if thread and thread.is_alive():
        return False
    server_states.setdefault(sid, {})["proc"] = None
    server_states.setdefault(sid, {})["thread"] = None
    return True

# End AI disclosure

def create_server(sid, name, stop_cmd, stype, software_type, version="latest", force_create=False):
    if os.path.exists(f"/servers/{sid}"):
        if not force_create:
            raise Exception("Server already exists")
        shutil.rmtree(f"/servers/{sid}")
    os.mkdir(f"/servers/{sid}")
    print("Downloading server...")
    cresp = os.system(f"cd /servers/{sid} && /app/serverconfigs/{software_type}/create.sh {sid} {version}")
    if cresp != 0:
        raise Exception("Failed to create server")
    print("Server created.")
    server = Server(id=sid, name=name, stop_cmd=stop_cmd, type=stype)
    db.session.add(server)
    db.session.commit()
    return server

class User(db.Model):
    id = db.Column(db.String(255), primary_key=True, unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    def generate_token(self):
        return jwt.encode({"usr": self.id}, app.config['SECRET_KEY'], algorithm="HS256")

class Server(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    name = db.Column(db.String(30), nullable=False)
    stop_cmd = db.Column(db.String(30), nullable=False)
    type = db.Column(db.String(5), nullable=False)
    thread = None
    proc = None

with app.app_context():
    print("Initializing database...")
    db.create_all()
    # Check if any servers exist, if not create a proxy
    print("Checking for existing servers...")
    if Server.query.count() == 0:
        print("No servers found, creating default proxy and lobby servers...")
        create_server(
            25565,
            "Proxy",
            "shutdown",
            "proxy",
            "proxy",
            "3.5.0-SNAPSHOT",
            force_create=True
        )
        create_server(
            30000,
            "Lobby",
            "stop",
            "lobby",
            "paper",
            "1.21.10",
            force_create=True
        )
    # Start lobby and proxy servers
    proxy_server = Server.query.filter_by(type="proxy").first()
    lobby_server = Server.query.filter_by(type="lobby").first()
    # If these dont exist, we just let it error out
    start_server(proxy_server)
    start_server(lobby_server)
    print("Servers started.")

def signal_handler(sig, frame):
    print("Stopping servers...")
    with app.app_context():
        for qserver in Server.query.all():
            print(f"Stopping server {qserver.name}...")
            stop_server(qserver)
            print(f"Server {qserver.name} stopped.")
    print("All servers stopped.")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Import routes
for root, _, files in os.walk("app/routes"):
    for file in files:
        if file.endswith(".py") and not file.startswith("__"):
            module_path = os.path.join(root, file).replace("/", ".").rstrip(".py")
            print(f"Importing module {module_path}...")
            importlib.import_module(module_path)
