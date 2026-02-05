from flask import render_template, redirect
from app import app, require_no_login, limiter, request, get_user, check_password, create_user, get_user_count
import random

with app.app_context():
    if get_user_count() == 0:
        adm_pwd = str(random.randbytes(16).hex())
        create_user("admin", adm_pwd)
        print(f"Created initial 'admin' user with password: {adm_pwd}")
        with open("/data/initial_admin_password.txt", "w", encoding="UTF-8") as f:
            f.write(adm_pwd)
        del adm_pwd
    elif get_user_count() == 1:
        with open("/data/initial_admin_password.txt", "r", encoding="UTF-8") as f:
            adm_pwd = f.read().strip()
        print(f"Initial password is: {adm_pwd}. Change it when possible.")

@app.route("/login")
@require_no_login
def login():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
@require_no_login
@limiter.limit("3 per minute")
def login_post():
    usr = get_user(request.form['id'])
    if not usr or not check_password(usr.password, request.form['password']):
        return render_template("login.html", error="Invalid username or password.")
    token = usr.generate_token()
    resp = redirect("/dashboard")
    resp.set_cookie("token", token, httponly=True, samesite="Lax")
    return resp

@app.route("/logout")
def logout():
    resp = redirect("/login")
    resp.set_cookie("token", "", expires=0)
    return resp