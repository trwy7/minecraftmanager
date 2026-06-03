import os
from flask import request, send_from_directory
from app import app, require_login, Server, make_backup, restore_backup, socketio

@app.route("/server/<int:server_id>/backups")
@require_login
def get_server_backups(server_id):
    server_dir = f"/backups/{str(server_id)}"
    listing = [{ # TODO: make just string
        'name': x,
    } for x in os.listdir(server_dir)]
    return {'files': listing}, 200

@socketio.on('create_backup')
def make_server_backup(data):
    server = Server.query.get(data.get('server_id'))
    if not server:
        return
    make_backup(server, name=data.get('name'))

@app.route("/server/<int:server_id>/backups/<string:filename>/restore", methods=['POST'])
@require_login
def restore_server_backup(server_id, filename):
    server = Server.query.get(server_id)
    if not server:
        return {'error': 'Server not found'}, 404
    restore_backup(server, name=filename)
    return "done"

@app.route("/server/<int:server_id>/backups/<string:filename>", methods=['GET', 'PUT', "DELETE"])
@require_login
def handle_server_backups(server_id, filename):
    server_dir = f"/backups/{str(server_id)}"
    file_path = os.path.join(server_dir, filename)
    if request.method == 'GET':
        if os.path.exists(file_path):
            return send_from_directory(server_dir, filename)
        else:
            return {'error': 'File not found'}, 404
    elif request.method == 'PUT':
        file = request.files.get('file')
        if not file:
            if request.json.get('new_name'):
                new_path = os.path.join(server_dir, request.json['new_name'])
                if os.path.exists(new_path):
                    return {'error': 'File or directory with new name already exists'}, 400
                os.rename(file_path, new_path)
                return {'message': 'File or directory renamed successfully'}, 200
        file.save(file_path)
        return {'message': 'File uploaded successfully'}, 200
    elif request.method == 'DELETE':
        if os.path.exists(file_path):
            os.remove(file_path)
            return {'message': 'File or directory deleted successfully'}, 200
        else:
            return {'error': 'File not found'}, 404
