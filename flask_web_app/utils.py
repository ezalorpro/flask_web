from flask_web_app.models import User
from wtforms import ValidationError

class EmailUniqueness(object):
    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        from flask_login import current_user
        temp = User.query.filter(User.email == field.data).first()
        if temp and not current_user.email == field.data:
            raise ValidationError(self.message)