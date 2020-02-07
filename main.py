import os
import random
import string
from datetime import datetime

import bcrypt
from flask import jsonify, request, render_template
from flask_login import login_user, login_required, logout_user, current_user
from flask_restful import Resource, Api 
from __init__ import app, db, login_manager
#from models import Events, Users, Categories, EventAnalytics, Ranks
from resources.mail.mailToken import generate_confirmation_token, confirm_token
from resources.mail.emailer import send_email

from api import user_api, administration_api, events_api, analytics_api, auth_api

config = os.getenv('ENV', 'dev')
if config == 'prod':
    app.config.from_object('config.ProductionConfig')
elif config == 'dev':
    app.config.from_object('config.DevelopmentConfig')

engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
Base = declarative_base()
Base.metadata.create_all(engine)

#Make Upload Folder 
upload_folder = app.config['UPLOAD_FOLDER']
if not os.path.exists(upload_folder):
    os.makedirs(upload_folder)

#Register all blueprints 
app.register_blueprint(user_api, url_prefix = "/user")
app.register_blueprint(administration_api, url_prefix = "/admin")
app.register_blueprint(events_api, url_prefix = "events")
app.register_blueprint(analytics_api, url_prefix = "/analytics")
app.register_blueprint(auth_api, url_prefix = "/auth")

@login_manager.user_loader
def load_user(user_id):
    return db.session.query(Users).filter(Users.id == int(user_id)).first()


# ---------------------------HELPER METHODS-------------------------------------------
def get_mobile_or_web_user():
    username = get_jwt_identity()
    user = None
    if username is not None:
        user = Users.get_user_by_email(username)
    return user


def rankAssocAdmin(user):
    #TODO: Add a function like get_user_by email for rank?
    rank = db.session.query(Ranks).filter(Ranks.uid == user.id).first().rank
    return rank == 1 or rank == 2

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
