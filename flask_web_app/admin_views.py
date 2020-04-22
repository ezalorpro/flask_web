import datetime
import json
import re
import os

import wtforms
from flask import flash, jsonify, redirect, render_template, request, url_for
from flask_admin import AdminIndexView, BaseView, expose, form, helpers
from flask_admin.contrib.sqla import ModelView
from flask_login import (current_user, login_required, login_url, login_user, logout_user)
from jinja2 import Markup
from sqlalchemy.event import listens_for
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from wtforms import validators

from flask_web_app import app, db, file_path, login_manager, op
from flask_web_app.forms import LoginForm, PlotingForm, RegistrationForm
from flask_web_app.models import User


class MyAdminIndexView(AdminIndexView):

    @expose("/")
    def index(self):
        return super(MyAdminIndexView, self).index()

    @expose("/logout/")
    def logout(self):
        logout_user()
        return redirect(url_for(".index"))

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("login.admin_login"))


class AdminLoginView(BaseView):

    @expose("/", methods=["GET", "POST"])
    def admin_login(self):
        form = LoginForm()
        if request.method == "POST":
            if helpers.validate_form_on_submit(form):
                user = User.query.filter(User.username == form.username.data).first()
                if user.is_admin:
                    login_user(user, remember=form.recordar.data)
                    if request.form.get("next"):
                        return redirect(request.form.get("next"))
                    return redirect(url_for("admin.index"))
                else:
                    flash("Solo administradores pueden acceder")
                    return self.render("admin/admin_login.html", form=form)
            else:
                return self.render("admin/admin_login.html", form=form)
        else:
            return self.render("admin/admin_login.html", form=form)

    def is_accessible(self):
        return not current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return """<h2> Acceso no autorizado </h2> <a href="/">Regresar</a>"""


class CustomPasswordField(wtforms.PasswordField):

    def populate_obj(self, obj, name):
        setattr(obj, name, generate_password_hash(self.data))


def prefix_name(obj, file_data):
    parts = op.splitext(file_data.filename)
    return secure_filename(obj.username + '-%s%s'%parts)


class UserView(ModelView):
    form_extra_fields = {
        "password_hash":
            CustomPasswordField("Contraseña",
                                validators=[validators.InputRequired()]),
        'avatar':
            form.ImageUploadField(
                'Avatar',
                base_path=file_path,
                namegen=prefix_name,
                url_relative_path='images/',
                thumbnail_size=(50,
                                50,
                                True)
            )
    }

    column_list = [
        "username",
        "email",
        "first_name",
        "last_name",
        "location",
        "gender",
        "information",
        "is_admin",
        "avatar"
    ]

    form_columns = [
        "username",
        "password_hash",
        "email",
        "first_name",
        "last_name",
        "location",
        "gender",
        "information",
        "is_admin",
        "avatar",
    ]

    form_widget_args = {
        "username": {
            "Autocomplete": "off"
        },
        "password_hash": {
            "Autocomplete": "off"
        },
        "email": {
            "Autocomplete": "off"
        },
    }

    def _list_thumbnail(self, context, model, name):
        if not model.avatar:
            return Markup(
                '<img src="%s">' % url_for('static',
                                           filename='images/default_thumb.png')
            )

        return Markup(
            '<img src="%s">' %
            url_for('static',
                    filename='images/' + form.thumbgen_filename(model.avatar))
        )

    column_formatters = {'avatar': _list_thumbnail}
    form_formatters = {'avatar': _list_thumbnail}

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin


class PostView(ModelView):
    form_args = dict(user=dict(label="Usuario", validators=[validators.DataRequired()]))
    form_columns = ["user", "title", "post_text"]
    form_widget_args = {
        "user": {
            "required": True
        },
        "post_date": {
            "readonly": True
        },
        "post_modified": {
            "readonly": True
        },
    }

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@listens_for(User, 'after_delete')
def del_user(mapper, connection, target):
    if target.avatar:
        # Delete image
        try:
            os.remove(op.join(file_path, target.avatar))
        except OSError:
            pass

        # Delete thumbnail
        try:
            os.remove(op.join(file_path, form.thumbgen_filename(target.avatar)))
        except OSError:
            pass
