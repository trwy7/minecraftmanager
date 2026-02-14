from app import app, Server, socketio, start_server, stop_server, run_command, require_login, send_stdin, delete_server
from flask import request

@socketio.on('start_server')
def handle_start_server(data):
    server_id = data.get('server_id')
    server = Server.query.get(server_id)
    if server:
        start_server(server)

@socketio.on('stop_server')
def handle_stop_server(data):
    server_id = data.get('server_id')
    server = Server.query.get(server_id)
    if server:
        stop_server(server)

@socketio.on('restart_server')
def handle_restart_server(data):
    server_id = data.get('server_id')
    server = Server.query.get(server_id)
    if server:
        print(f"Restarting server {server.name}...")
        stop_server(server)
        print(f"Server {server.name} stopped starting back up...")
        start_server(server)

@socketio.on('send_command')
def handle_send_command(data):
    server_id = data.get('server_id')
    command = data.get('command')
    server = Server.query.get(server_id)
    if server and command:
        send_stdin(server, command + "\n")

@app.route('/servers/<int:server_id>/command', methods=['POST'])
@require_login
def run_server_command(server_id):
    server = Server.query.get(server_id)
    if not server:
        return {'error': 'Server not found'}, 404

    command = request.json.get('command')
    if not command:
        return {'error': 'No command provided'}, 400

    output = run_command(server, command)
    return {'output': output}, 200

@app.route('/server/<int:server_id>', methods=['DELETE'])
@require_login
def delete_server_route(server_id):
    server = Server.query.get(server_id)
    if not server:
        return {'error': 'Server not found'}, 404
    try:
        delete_server(server)
    except ValueError as e:
        return str(e), 400
    return {'message': 'Server deleted successfully'}, 200