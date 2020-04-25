import datetime
import enum
from hashlib import md5

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import types

from flask_web_app import db, login_manager

# class ChoiceType(types.TypeDecorator):

#     impl = types.String

#     def __init__(self, choices, **kw):
#         self.choices = dict(choices)
#         super(ChoiceType, self).__init__(**kw)

#     def process_bind_param(self, value, dialect):
#         return [k for k, v in self.choices.items() if v == value][0]

#     def process_result_value(self, value, dialect):
#         return self.choices[value]

class GenderderEnum(enum.Enum):
    nulo = "--"
    hombre = "Hombre"
    mujer = "Mujer"

class RoleEnum(enum.Enum):
    regular_user = "Usuario regular"
    editor = "Editor"
    admin = "Admin"

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String, index=True, unique=True, nullable=False)
    first_name = db.Column(db.String, index=True)
    last_name = db.Column(db.String, index=True)
    email = db.Column(db.String, index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    avatar = db.Column(db.String, index=True)
    location = db.Column(db.String, index=True)
    gender = db.Column(db.Enum(GenderderEnum), index=True)
    information = db.Column(db.Text, index=True)
    role = db.Column(db.Enum(RoleEnum), index=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<Usuario: {self.username}>"


class PostModel(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.String, index=True, nullable=False, unique=True)
    post_text = db.Column(db.Text, index=True)
    post_date = db.Column(
        db.DateTime, index=True, nullable=False, default=datetime.datetime.utcnow
    )
    post_modified = db.Column(
        db.DateTime,
        index=True,
        nullable=False,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
    )
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"))
    user = db.relationship(
        "User", backref=db.backref("postmodel", lazy="dynamic", passive_deletes=True)
    )


class ImagePostModel(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    path = db.Column(db.String, index=True, unique=True)
    post_id = db.Column(db.Integer, db.ForeignKey("post_model.id", ondelete="CASCADE"))
    post = db.relationship(
        "PostModel", backref=db.backref("imagepostmodel", lazy="dynamic", passive_deletes=True)
    )


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
