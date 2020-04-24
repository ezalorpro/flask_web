import datetime
import enum
from hashlib import md5

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from flask_web_app import db, login_manager


class GenderderEnum(enum.Enum):
    nulo = "--"
    hombre = "Hombre"
    mujer = "Mujer"


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
    is_admin = db.Column(db.Boolean, index=True)

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


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
