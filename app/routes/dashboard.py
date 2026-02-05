from flask import render_template
from app import app, require_login, get_servers, is_server_running

@app.route("/dashboard")
@require_login
def dashboard():
    return render_template("dashboard.html", servers=get_servers(), is_server_running=is_server_running)