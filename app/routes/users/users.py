from flask import render_template, request
from app import app, require_login, User, create_user, change_password, delete_user

@app.route("/users")
@require_login
def users():
    return render_template("users.html", users=User.query.all())

@app.route("/adduser", methods=['POST'])
@require_login
def adduser():
    create_user(request.json['name'], request.json['pwd'])
    return {"status": "ok"}

@app.route("/changepwd", methods=['POST'])
@require_login
def chpwd():
    change_password(request.json['user'], request.json['pwd'])
    return {"status": "ok"}

@app.route("/deleteuser", methods=['POST'])
@require_login
def deluser():
    delete_user(request.json['user'])
    return {"status": "ok"}