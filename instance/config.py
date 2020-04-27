import os
import os.path as op

from flask_web_app import file_path

basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = True
SQLALCHEMY_ECHO = True
SQLALCHEMY_DATABASE_URI = "postgresql:///flask_web"
SQLALCHEMY_TRACK_MODIFICATIONS = True
FLASK_ADMIN_SWATCH = "paper"
SECRET_KEY = "pelispedia"
UPLOADED_PHOTOS_DEST = file_path
