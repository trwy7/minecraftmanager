from flask import render_template
from app import app, require_login, get_servers, get_server_status

@app.route("/dashboard")
@require_login
def dashboard():
    return render_template("dashboard.html", servers=get_servers(), get_server_status=get_server_status)