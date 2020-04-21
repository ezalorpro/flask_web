import os
basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = False
SQLALCHEMY_ECHO = False
SQLALCHEMY_DATABASE_URI = 'sqlite:////' + basedir + 'flask_web.db'
FLASK_ADMIN_SWATCH = 'cerulean'
SECRET_KEY = 'pelispedia'
