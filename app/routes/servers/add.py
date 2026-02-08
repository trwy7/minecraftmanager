from app import app, create_server, get_next_free_server_id, require_login
from flask import request, render_template, redirect

@app.route("/addserver")
@require_login
def add_server():
    return render_template("addserver.html")

@app.route("/addserver", methods=['POST'])
@require_login
def add_server_post():
    create_server(
        get_next_free_server_id(),
        request.form['name'],
        "stop",
        "game",
        request.form['type'],
        request.form['version'],
    )
    return redirect("/dashboard")