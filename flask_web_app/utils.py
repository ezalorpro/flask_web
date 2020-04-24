import os.path as op

import wtforms
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from wtforms import ValidationError

from flask_web_app.models import User, PostModel


class CustomPasswordField(wtforms.PasswordField):
    def populate_obj(self, obj, name):
        if not obj.check_password(self.data) and self.data:
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
