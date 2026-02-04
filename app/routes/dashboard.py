from flask import render_template
from app import app, require_login

@app.route("/dashboard")
@require_login
def dashboard():
    return render_template("dashboard.html")