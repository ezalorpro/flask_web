import json
import re

import wtforms
from flask import flash, jsonify, redirect, render_template, request, url_for
from flask_admin import AdminIndexView, BaseView, expose, helpers
from flask_admin.contrib.sqla import ModelView
from flask_login import (current_user, login_required, login_url, login_user, logout_user)
from werkzeug.security import check_password_hash, generate_password_hash
from wtforms import validators

from flask_web_app import app, db, login_manager
from flask_web_app.forms import LoginForm, PlotingForm, RegistrationForm
from flask_web_app.models import User


class MyAdminIndexView(AdminIndexView):

    @expose('/')
    def index(self):
        return super(MyAdminIndexView, self).index()

    @expose('/logout/')
    def logout(self):
        logout_user()
        return redirect(url_for('.index'))

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login.admin_login'))


class AdminLoginView(BaseView):

    @expose('/', methods=['GET', 'POST'])
    def admin_login(self):
        form = LoginForm()
        if request.method == 'POST':
            if helpers.validate_form_on_submit(form):
                user = User.query.filter(User.username == form.username.data).first()
                if user.is_admin:
                    login_user(user, remember=form.recordar.data)
                    if request.form.get("next"):
                        return redirect(request.form.get("next"))
                    return redirect(url_for('admin.index'))
                else:
                    flash('Solo administradores pueden acceder')
                    return self.render('admin/admin_login.html', form=form)
            else:
                return self.render('admin/admin_login.html', form=form)
        else:
            return self.render('admin/admin_login.html', form=form)

    def is_accessible(self):
        return not current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return '''<h2> Acceso no autorizado </h2> <a href="/">Regresar</a>'''


class CustomPasswordField(wtforms.PasswordField):

    def populate_obj(self, obj, name):
        setattr(obj, name, generate_password_hash(self.data))


class UserView(ModelView):
    form_extra_fields = {
        'password_hash':
            CustomPasswordField('Contraseña',
                                validators=[validators.InputRequired()])
    }
    column_list = [
        'username',
        'email',
        'first_name',
        'last_name',
        'location',
        'gender',
        'information',
        'is_admin'
    ]

    form_columns = [
        'username',
        'password_hash',
        'email',
        'first_name',
        'last_name',
        'location',
        'gender',
        'information',
        'is_admin'
    ]

    form_widget_args = {
        'username': {
            'Autocomplete': "off"
        },
        'password_hash': {
            'Autocomplete': "off"
        },
        'email': {
            'Autocomplete': "off"
        },
    }

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin


class PostView(ModelView):
    form_args = dict(user=dict(label='Usuario', validators=[validators.DataRequired()]))
    form_columns = ['user', 'title', 'post_text']
    form_widget_args = {
        'user': {
            'required': True
        },
        'post_date': {
            'readonly': True
        },
        'post_modified': {
            'readonly': True
        },
    }

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
