import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

if os.environ.get("IN_DOCKER", "false").lower() != "true":
    # Bad practice, but ensures that the app is only run in Docker
    raise EnvironmentError("The application must be run inside a Docker container.")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////data/db.sqlite3'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
