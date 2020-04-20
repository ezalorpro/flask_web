from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf import CSRFProtect


app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py')

csrf = CSRFProtect(app)
csrf.init_app(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
admin = Admin(app, name='flask_web', template_mode='bootstrap3')
login = LoginManager(app)
login.init_app(app)

from flask_web_app import views, models, forms
