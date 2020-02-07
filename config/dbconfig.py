# Databse configuration information
from flask import app

pg_config = {
    'user' : 'appusr',
    'passwd' : 'appusr1',
    'dbname' : 'appdb',
}

app.config['TESTING'] = False
