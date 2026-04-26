#import eventlet
from app import app, socketio

if __name__ == "__main__":
    print("Starting web server...")
    # If someone knows how to get waitress to work with socketio, please tell me
    #waitress.serve(app, host="0.0.0.0", port=7843)
    socketio.run(app, host="0.0.0.0", port=7843)