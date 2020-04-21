from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py')

csrf = CSRFProtect(app)
csrf.init_app(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.init_app(app)
# toolbar = DebugToolbarExtension(app)

from flask_web_app import admin_views

admin = Admin(app,
              name='Flask Web',
              template_mode='bootstrap3',
              index_view=admin_views.MyAdminIndexView()
              )


from flask_web_app import views, models, forms, admin_views

admin.add_view(admin_views.UserView(models.User, db.session))
admin.add_view(admin_views.AdminLoginView(endpoint='login'))
