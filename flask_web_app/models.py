from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from flask_web_app import db
from flask_web_app import login
import enum

class GenderderEnum(enum.Enum):
    hombre = 'Hombre'
    mujer = 'Mujer'


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String, index=True, unique=True, nullable=False)
    first_name = db.Column(db.String, index=True)
    last_name = db.Column(db.String, index=True)
    email = db.Column(db.String, index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    location = db.Column(db.String, index=True)
    gender = db.Column(db.Enum(GenderderEnum), index=True)
    information = db.Column(db.String, index=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # def avatar(self, size):
    #     avatar_hash = md5(self.email.lower().encode('utf-8')).hexdigest()
    #     return f'https://www.gravatar.com/avatar/{avatar_hash}?d=identicon&s={size}'

    def __repr__(self):
        return f'<Usuario {self.username}>'


@login.user_loader
def load_user(id):
    return User.query.get(int(id))