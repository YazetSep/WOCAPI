class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = "Kx5mjuptrKFzknp7RIEQ3Ed2XD9hZniO"
    SECURITY_PASSWORD_SALT = "WOC_IS_LIFE10"
 
class ProductionConfig(Config):
    DATABASE_URI = 'mysql://user@localhost/foo'
    mail_config =  {
        "MAIL_SERVER": 'smtp.google.com',
        "MAIL_PORT": 465,
        "MAIL_USE_TLS": False,
        "MAIL_USE_SSL": True,
        "MAIL_USERNAME": 'hacksquadpr@gmail.com',
        "MAIL_PASSWORD": 'pass'
    }
    pg_config = {
        'user': 'postgres',
        'password': 'LX2GkLPmjkU*xCMgRoGh',
        'dbname': 'woctest',
        'host': 'wocpr.com',
        'port': '5432'
    }
    SQLALCHEMY_DATABASE_URI = 'postgresql://%(user)s:\%(password)s@%(host)s:%(port)s/%(dbname)s' % pg_config
    UPLOAD_FOLDER = "/var/www/html/upload" 

class DevelopmentConfig(Config):
    DEBUG = True
    #Put fake smtp server conf here 
    UPLOAD_FOLDER = "upload/" 
    mail_config =  {
        "MAIL_SERVER": 'smtp.test.com',
        "MAIL_PORT": 465,
        "MAIL_USE_TLS": False,
        "MAIL_USE_SSL": True,
        "MAIL_USERNAME": 'fakeemail@gmail.com',
        "MAIL_PASSWORD": 'fake_password'
    }
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/dev.db' 

class TestingConfig(Config):
    TESTING = True
    DEBUG = True 
    WTF_CSRF_ENABLED = False 
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:' 


        
