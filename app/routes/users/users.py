from flask import render_template, request
from app import app, require_login, User, create_user, get_user

@app.route("/users")
@require_login
def users():
    return render_template("users.html", users=User.query.all())

@app.route("/adduser", methods=['POST'])
@require_login
def adduser():
    create_user(request.json['name'], request.json['pwd'])
    return {"status": "ok"}