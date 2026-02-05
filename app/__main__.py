import waitress
from app import app

if __name__ == "__main__":
    print("Starting server...")
    waitress.serve(app, host="0.0.0.0", port=7843)
