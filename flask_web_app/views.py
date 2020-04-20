from flask import render_template, url_for, request, redirect, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user, login_user, logout_user, login_required
from flask_web_app import app, admin, db
from flask_admin.contrib.sqla import ModelView
from flask_web_app.models import User
from flask_web_app.forms import RegistrationForm, LoginForm
from wtforms import validators
import wtforms
import re

EMAIL_REGX = r'[^@]+@[^@]+\.[^@]+'



class CustomPasswordField(wtforms.PasswordField):

    def populate_obj(self, obj, name):
        setattr(obj, name, generate_password_hash(self.data))


class UserView(ModelView):
    form_extra_fields = {
        'password_hash':
            CustomPasswordField('Contraseña', validators=[validators.InputRequired()])
    }


admin.add_view(UserView(User, db.session))


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = User.query.filter(User.username == form.username.data).first()
        login_user(user, remember=form.recordar.data)
        return redirect(url_for('home'))
    else:
        return render_template('login.html', form=form)

@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    form = RegistrationForm()
    data = request.args
    if request.method == 'POST' and form.validate_on_submit():
        user = User()
        form.populate_obj(user)
        user.set_password(form.password1.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    elif data:
        if data['tipo'] == 'username':
            data = {
                'flag':
                    bool(User.query.filter(User.username == data['name']).first())
            }
        elif data['tipo'] == 'email':
            if not bool(re.match(EMAIL_REGX, data['email'])):
                data = {
                    'flag': False,
                    'info': 'Ingrese una dirección de correo electrónico válida.',
                }
            elif bool(User.query.filter(User.email == data['email']).first()):
                data = {
                    'flag': False,
                    'info': 'Correo electronico ya registrado, ingrese otro',
                }
            else:
                data = {
                    'flag': True,
                    'info': '',
                }

        return jsonify(data)
    else:
        return render_template('registrar.html', form=form)