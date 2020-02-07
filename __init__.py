from flask import Flask
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base

app = Flask(__name__, template_folder='template')
db = SQLAlchemy(app)
jwt = JWTManager(app)
Base = declarative_base()
