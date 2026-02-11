import os
import shutil
from flask import request, send_from_directory
from app import app

@app.route("/server/<int:server_id>/files/<path:filename>", methods=['GET', 'PUT', 'POST', "DELETE"])
def handle_server_files(server_id, filename):
    server_dir = f"/servers/{str(server_id)}"
    file_path = os.path.join(server_dir, filename)
    if request.method == 'GET':
        if os.path.exists(file_path):
            if os.path.isdir(file_path):
                listing = [{
                    'name': x,
                    'type': 'dir' if os.path.isdir(os.path.join(file_path, x)) else 'file'
                } for x in os.listdir(file_path)]
                listing.sort(key=lambda x: (not os.path.isdir(os.path.join(file_path, x['name'])), x['name'].lower()))
                return {'files': listing}, 200
            return send_from_directory(server_dir, filename)
        else:
            return {'error': 'File not found'}, 404
    elif request.method == 'PUT':
        file = request.files.get('file')
        if not file:
            return {'error': 'No file uploaded'}, 400
        file.save(file_path)
        return {'message': 'File uploaded successfully'}, 200
    elif request.method == 'POST':
        os.mkdir(file_path, exist_ok=True)
        return {'message': 'Directory created successfully'}, 200
    elif request.method == 'DELETE':
        if os.path.exists(file_path):
            if os.path.isdir(file_path):
                shutil.rmtree(file_path)
            else:
                os.remove(file_path)
            return {'message': 'File or directory deleted successfully'}, 200
        else:
            return {'error': 'File not found'}, 404

@app.route("/server/<int:server_id>/files/", methods=['GET'])
def get_server_files(server_id):
    server_dir = f"/servers/{str(server_id)}"
    listing = [{
        'name': x,
        'type': 'dir' if os.path.isdir(os.path.join(server_dir, x)) else 'file'
    } for x in os.listdir(server_dir)]
    listing.sort(key=lambda x: (not os.path.isdir(os.path.join(server_dir, x['name'])), x['name'].lower()))
    return {'files': listing}, 200