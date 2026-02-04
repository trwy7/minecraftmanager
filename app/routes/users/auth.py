from flask import request, render_template, redirect
import requests
from app import app, require_no_login, User

@app.route("/login")
@require_no_login
def login():
    return render_template("auth/login.html")

@app.route("/requestaccount")
@require_no_login
def request_account(uid):
    return render_template("auth/request_account.html")
