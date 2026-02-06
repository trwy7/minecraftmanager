#import eventlet
from app import app, socketio

if __name__ == "__main__":
    print("Starting server...")
    #waitress.serve(app, host="0.0.0.0", port=7843)
    # If someone knows how to get waitress to work with socketio, please tell me
    #eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 7843)), app)
    socketio.run(app, host="0.0.0.0", port=7843)