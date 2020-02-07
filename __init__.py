import os
from flask_jwt import JWT
from flask import Flask
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, jwt_optional
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from flask_login import LoginManager
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from flask_mail import Mail, Message
from flask_restful import Api
from flask_cors import CORS

app = Flask(__name__, template_folder='templates')
api = Api(app) 
CORS(app)


db = SQLAlchemy(app)
jwt = JWTManager(app)

login_manager = LoginManager()
login_manager.init_app(app)
Session = sessionmaker(autoflush=False)
def authenticate(email, password):
    user = Users.get_user_by_email(username)
    if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        login_user(user)
        return user
    else:
        return 'bro what'

def identity(payload):
    user_id = payload['identity']
    user = Users.get_user_by_email(username)
    return user


jwt = JWT(app, authenticate, identity)

mail = Mail(app)


