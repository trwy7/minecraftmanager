import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////data/db.sqlite3'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.String(255), primary_key=True, unique=True, nullable=False)

class Server(db.Model):
    id = db.Column(db.String(255), primary_key=True, unique=True, nullable=False)
    name = db.Column(db.String(30), nullable=False)
    stop_cmd = db.Column(db.String(30), nullable=False)
    type = db.Column(db.String(5), nullable=False)
