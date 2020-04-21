import json
import re

import wtforms
from flask import jsonify, redirect, render_template, request, url_for
from flask_admin.contrib.sqla import ModelView
from flask_login import (current_user, login_required, login_url, login_user,
                         logout_user)
from werkzeug.security import check_password_hash, generate_password_hash
from wtforms import validators

from bokeh import plotting as plt
from bokeh.embed import components
from flask_web_app import admin, app, db, login_manager
from flask_web_app.forms import LoginForm, PlotingForm, RegistrationForm
from flask_web_app.models import User


EMAIL_REGX = r'[^@]+@[^@]+\.[^@]+'


@app.route('/')
def home():
    return render_template('home.html')


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(login_url('login', request.url))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter(User.username == form.username.data).first()
            login_user(user, remember=form.recordar.data)
            if request.form.get("next"):
                return redirect(request.form.get("next"))
            return redirect(url_for('home'))
        else:
            return render_template('login.html', form=form)
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
                'flag': bool(User.query.filter(User.username == data['name']).first())
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


@app.route('/ploting', methods=['GET', 'POST'])
@login_required
def ploting():
    if request.method == 'POST':
        x_data = json.loads(request.form['x_points'])
        y_data = json.loads(request.form['y_points'])

        p = plt.figure(sizing_mode='scale_width')
        p.line(x_data, y_data)

        script_bok, div_bok = components(p)
        response = {
            'script_bok': script_bok,
            'div_bok': div_bok
        }
        return script_bok + div_bok
    else:
        form = PlotingForm()
        x_data = [0]
        y_data = [0]

        p = plt.figure(sizing_mode='scale_width')
        p.line(x_data, y_data)
        script_bok, div_bok = components(p)
        context={
            'form': form,
            'div_bok': div_bok,
            'script_bok': script_bok
        }
        return render_template('ploting.html', **context)
