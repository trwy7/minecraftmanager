from app import app, Server, require_login, get_server_status
from flask import render_template

@app.route('/server/<int:server_id>', methods=['GET'])
@require_login
def get_server_info(server_id):
    server = Server.query.get(server_id)
    if not server:
        return {'error': 'Server not found'}, 404

    return render_template('server.html', server=server, server_status=get_server_status(server))
