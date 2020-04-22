import os
import os.path as op
from flask_web_app import file_path

basedir = os.path.abspath(os.path.dirname(__file__))
file_path = op.join(op.dirname(__file__), 'static/images')

DEBUG = False
SQLALCHEMY_ECHO = False
SQLALCHEMY_DATABASE_URI = "postgresql:///flask_web"
FLASK_ADMIN_SWATCH = 'cerulean'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = 'pelispedia'
UPLOADED_PHOTOS_DEST = file_path