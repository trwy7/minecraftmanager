from flask import render_template
from app import app, require_login, User
import random

@app.route("/users")
@require_login
def users():
    return render_template("users.html", users=User.query.all())
