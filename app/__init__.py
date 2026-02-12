# pylint: disable=missing-function-docstring, missing-class-docstring, wrong-import-position, wrong-import-order
from gevent import monkey, signal_handler
monkey.patch_all()
import os
import sys
import functools
import importlib
import shutil
import threading
import subprocess
import time
import re
import toml
import jwt
import signal
from flask import Flask, request, redirect
from flask_limiter import Limiter
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from rcon.source import Client
from rcon.exceptions import EmptyResponse

app = Flask(__name__, template_folder="pages", static_folder="static")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////data/db.sqlite3'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "ChangeM3P13ase")
app.config['SERVER_OWNER'] = os.environ.get('SERVER_OWNER')
if os.environ.get('ENV_MODE') == "dev":
    print("Running in dev mode, enabling auto reload")
    app.config['TEMPLATES_AUTO_RELOAD'] = True

db = SQLAlchemy(app)
limiter = Limiter(app=app, key_func=lambda: request.remote_addr, default_limits=["100/minute", "5/second"], storage_uri="memory://")
socketio = SocketIO(app, cors_allowed_origins="*")
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

@app.after_request
def prevent_caching(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

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

def get_next_free_server_id():
    existing_ids = {server.id for server in Server.query.all()}
    for i in range(30001, 30100):
        if i not in existing_ids:
            return i
    raise Exception("No free server IDs available") # if you have more than 100 servers, use pterodactyl

def get_servers():
    return {server: server_states.get(server.id, {}) for server in Server.query.all()}

def get_server_status(server):
    return {
        "running": is_server_running(server),
        "fully_started": server_states.get(server.id, {}).get("fully_started", False)
    }

def get_server_output(server, tail=100):
    log_path = f"/servers/{server.id}/output.log"
    if not os.path.exists(log_path):
        return ""
    with open(log_path, "r") as f:
        lines = f.readlines()
        return "".join(lines[-tail:])

def run_command(server, command):
    print(f"Running command '{command}' on '{server.name}'...")
    if not is_server_running(server):
        return None
    with Client('127.0.0.1', server.id + 1000, passwd='mcmanager') as client:
        try:
            response = client.run(*command.split(" "))
        except EmptyResponse:
            # why does this not just return none by default
            response = None
        except ConnectionRefusedError:
            print(f"Failed to connect to server {server.name} for command '{command}'. RCON is likely not initialized yet.")
            return None
    return response

def update_proxy_config(server):
    if os.path.exists(f"/servers/{server.id}/velocity.toml"):
        with open(f"/servers/{server.id}/velocity.toml", "r") as f:
            config = toml.load(f)
        config["player-info-forwarding-mode"] = "modern"
        config["servers"] = {}
        config["forced-hosts"] = {}
        for qserver in Server.query.filter(Server.type != "proxy").all():
            config["servers"][qserver.name] = "127.0.0.1:" + str(qserver.id)
            if os.environ.get("BASE_DOMAIN"):
                print(f"Adding forced-hosts config for {qserver.name} with domain {qserver.name + '.' + os.environ['BASE_DOMAIN']}")
                config["forced-hosts"][qserver.name + "." + os.environ["BASE_DOMAIN"]] = qserver.name
        config["servers"]['try'] = ["lobby"]
        with open(f"/servers/{server.id}/velocity.toml", "w") as f:
            toml.dump(config, f)
        if is_server_running(server):
            run_command(server, "velocity reload")

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
    if not os.path.exists(cmd):
        print(f"Run command {cmd} does not exist for server {server.name}")
        send_update("server_stopped", {"server_id": server.id})
        send_update("server_output", {"server_id": server.id, "output": f"Run command {cmd.removeprefix(cwd)} not found. Server cannot be started.\n"})
        return
    # Run without a shell to ensure stdout is captured correctly
    with subprocess.Popen(
        [cmd],
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=False
    ) as proc:
        send_update("server_started", {"server_id": server.id})
        # store the proc in the shared server state
        server_states.setdefault(sid, {})["proc"] = proc
        log_path = f"{cwd}/output.log"
        with open(log_path, "wb") as f:
            for line in iter(proc.stdout.readline, b""):
                #print(f"[{server.name}] {line.decode()}", end="")
                if len(authenticated_clients) != 0:
                    send_update("server_output", {"server_id": server.id, "output": line.decode()})
                if not server_states.get(sid, {}).get("fully_started"):
                    if re.search(rb"Done \(.+?\)!", line):
                        server_states.setdefault(sid, {})["fully_started"] = True
                        send_update("server_fully_started", {"server_id": server.id})
                f.write(line)
                f.flush()
            f.write(b"[mcm] Server process ended.\n")
        proc.wait()
        # clear the proc when finished
        server_states.setdefault(sid, {})["proc"] = None
        server_states.setdefault(sid, {})["fully_started"] = False
        send_update("server_stopped", {"server_id": server.id})

def start_server(server):
    """Start the server in a background thread if not already running."""
    print(f"Starting server {server.name}...")
    sid = server.id
    thread = server_states.get(sid, {}).get("thread")
    if thread and thread.is_alive():
        return True
    thread = threading.Thread(target=run_server, daemon=True, args=(server,))
    server_states.setdefault(sid, {})["thread"] = thread
    server_states.setdefault(sid, {})["fully_started"] = False
    if server.type == "proxy":
        print(f"Server {server.name} is a proxy, updating config.")
        update_proxy_config(server)
    thread.start()
    return thread

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
        proc.wait(timeout=60)
    socketio.sleep(1)
    thread = server_states.get(sid, {}).get("thread")
    if thread and thread.is_alive():
        if proc:
            print(f"Server {server.name} did not stop gracefully, killing process...")
            proc.kill()
    server_states.setdefault(sid, {})["proc"] = None
    server_states.setdefault(sid, {})["thread"] = None
    return True

# End AI disclosure

def create_server(sid, name, stop_cmd, stype, software_type, version="latest", force_create=False):
    # Name has to be lowercase letters
    name = name.strip().lower()
    # Replace spaces with dashes
    name = name.replace(" ", "-")
    # Remove any characters that are not lowercase letters, numbers, or dashes
    name = "".join(c for c in name if (c.isalnum() and not c.isdigit()) or c == "-")
    if os.path.exists(f"/servers/{sid}"):
        if not force_create:
            raise Exception("Server already exists")
        shutil.rmtree(f"/servers/{sid}")
    os.mkdir(f"/servers/{sid}")
    print("Downloading server...")
    cresp = os.system(f"cd /servers/{sid} && /app/serverconfigs/{software_type}/create.sh {sid} {version}")
    if cresp != 0:
        raise Exception("Failed to create server")
    print("Server created. Running initial setup...")
    server = Server(id=sid, name=name, stop_cmd=stop_cmd, type=stype)
    db.session.add(server)
    db.session.commit()
    start_server(server)
    while not server_states.get(sid, {}).get("fully_started"):
        if not server_states.get(sid, {}).get("thread") or not server_states[sid]["thread"].is_alive():
            print("Server failed to start.")
            raise Exception("Server failed to start after creation")
        time.sleep(1)
    time.sleep(1)
    # Server on configuration here
    if app.config['SERVER_OWNER']:
        if stype == "proxy":
            rs = run_command(server, "lpv user " + app.config['SERVER_OWNER'] + " permission set * true")
        else:
            rs = run_command(server, "lp user " + app.config['SERVER_OWNER'] + " permission set * true")
        print(rs)
    time.sleep(1)
    stop_server(server)
    update_proxy_config(Server.query.filter_by(id=25565).first())
    return server

def delete_server(server):
    stop_server(server)
    if os.path.exists(f"/servers/{server.id}"):
        shutil.rmtree(f"/servers/{server.id}")
    db.session.delete(server)
    db.session.commit()
    update_proxy_config(Server.query.filter_by(id=25565).first())

authenticated_clients = []
def send_update(event, data):
    if len(authenticated_clients) == 0:
        return
    with app.app_context():
        for sid in authenticated_clients:
            emit(event, data, broadcast=True, include_self=True, namespace="/", to=sid)

class User(db.Model):
    id = db.Column(db.String(255), primary_key=True, unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    def generate_token(self):
        return jwt.encode({"usr": self.id}, app.config['SECRET_KEY'], algorithm="HS256")

class Server(db.Model):
    # TODO: File browser
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    name = db.Column(db.String(30), unique=True, nullable=False)
    stop_cmd = db.Column(db.String(30), nullable=False)
    type = db.Column(db.String(5), nullable=False)
    thread = None
    proc = None

with app.app_context():
    print("Initializing database...")
    db.create_all()
    # Check if any servers exist, if not, create a proxy
    print("Checking for existing servers...")
    if Server.query.count() == 0:
        print("No servers found, creating default proxy and lobby servers...")
        proxy = create_server(
            25565,
            "proxy",
            "shutdown",
            "proxy",
            "proxy",
            "3.5.0-SNAPSHOT",
            force_create=True
        )
        create_server(
            30000,
            "lobby",
            "stop",
            "lobby",
            "paper",
            "1.21.10",
            force_create=True
        )
    # Start all servers

def start_all_servers():
    with app.app_context():
        print("Starting all servers...")
        for server in Server.query.all():
            print(f"Starting server {server.name}...")
            start_server(server)
            while not server_states.get(server.id, {}).get("fully_started"):
                if not server_states.get(server.id, {}).get("thread") or not server_states[server.id]["thread"].is_alive():
                    print(f"Server {server.name} failed to start.")
                    break
                time.sleep(1)
            print(f"Server {server.name} started.")

threading.Thread(target=start_all_servers, daemon=True).start()

def stop_all_servers():
    with app.app_context():
        print("Stopping all servers...")
        tlist = []
        for server in Server.query.all():
            # Start stopping all servers
            print(f"Stopping server {server.name}...")
            t = threading.Thread(target=stop_server, args=(server,), daemon=True)
            t.start()
            tlist.append(t)
        for t in tlist:
            t.join()
        print("All servers stopped.")

def stop_signal_handler():
    print("Received shutdown signal, stopping all servers...")
    stop_all_servers() # Docker should kill this process after 60 seconds if there is a non responding server
    print("All servers stopped. Exiting.")
    sys.exit(0)

signal_handler(signal.SIGINT, stop_signal_handler)

@socketio.on("connect")
def handle_connect(auth):
    token = auth.get("token") if auth else None
    if not token:
        print("No auth token provided, rejecting SocketIO connection")
        return False
    try:
        cusr = jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")['usr']
        usr = get_user(cusr)
        if not usr:
            print("Invalid user in token, rejecting SocketIO connection")
            return False
        print(f"User {usr.id} connected via SocketIO")
        authenticated_clients.append(request.sid)
        socketio.emit("auth_success", {"message": "Authenticated successfully"}, to=request.sid)
    except jwt.exceptions.InvalidSignatureError:
        return False

@socketio.on("disconnect")
def handle_disconnect():
    print(f"Client {request.sid} disconnected from SocketIO")
    if request.sid in authenticated_clients:
        authenticated_clients.remove(request.sid)

# Import routes
for root, _, files in os.walk("app/routes"):
    for file in files:
        if file.endswith(".py") and not file.startswith("__"):
            module_path = os.path.join(root, file).replace("/", ".").rstrip(".py")
            print(f"Importing module {module_path}...")
            importlib.import_module(module_path)
