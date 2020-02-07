from flask import Flask
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from config.config import pg_config
from flask_login import LoginManager
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from flask_mail import Mail, Message

app = Flask(__name__, template_folder='templates')
db = SQLAlchemy(app)
jwt = JWTManager(app)
Base = declarative_base()

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:\
%(password)s@%(host)s:%(port)s/%(dbname)s' % pg_config
app.config['SECRET_KEY'] = "Kx5mjuptrKFzknp7RIEQ3Ed2XD9hZniO"
app.config['SECURITY_PASSWORD_SALT'] = "WOC_IS_LIFE10"
login_manager = LoginManager()
login_manager.init_app(app)
Session = sessionmaker(autoflush=False)
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

app.config['MAIL_DEFAULT_SENDER'] = 'noreply@wocpr.com'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = "hacksquadpr@gmail.com"#os.environ.get('EMAIL_USER')
app.config['MAIL_PASSWORD'] = "ignjfpslqavizhur"#os.environ.get('EMAIL_PASS')
mail = Mail(app)

