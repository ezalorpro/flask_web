import os.path as op

import wtforms
from functools import wraps
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from wtforms import ValidationError
from flask import current_app

from flask_web_app import login_manager
from flask_login import current_user
from flask_web_app.models import User, PostModel


class CustomPasswordField(wtforms.PasswordField):
    def populate_obj(self, obj, name):
        if obj.password_hash:
            if not obj.check_password(self.data) and self.data:
                setattr(obj, "password_hash", generate_password_hash(self.data))
        else:
            if self.data:
                setattr(obj, "password_hash", generate_password_hash(self.data))

class EmailUniqueness(object):
    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        from flask_login import current_user

        temp = User.query.filter(User.email == field.data).first()
        if temp and not current_user.email == field.data:
            raise ValidationError(self.message)


class PostTitleUniqueness(object):
    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        temp = PostModel.query.filter_by(title=field.data).first()
        if temp:
            if not temp.id == (int(form.post_id) if form.post_id is not None else None):
                raise ValidationError(self.message)


def prefix_name(obj, file_data):
    parts = op.splitext(file_data.filename)
    return secure_filename(obj.username + "-%s%s" % parts)


def login_required(role="regular_user"):
    def roles_wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return login_manager.unauthorized()
            if (current_user.role not in role) and (role != "regular_user"):
                return login_manager.unauthorized()
            return fn(*args, **kwargs)

        return decorated_view

    return roles_wrapper
