from flask import render_template
from flask_web_app import app, admin, db
from flask_admin.contrib.sqla import ModelView
from flask_web_app.models import User

admin.add_view(ModelView(User, db.session))

@app.route('/')
def home():
    return render_template('home.html')
