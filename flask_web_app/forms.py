from flask_wtf import FlaskForm
from flask_wtf import file
from flask_web_app.models import User
from flask_web_app.utils import EmailUniqueness
from flask_web_app import photos

import wtforms
from wtforms import validators, ValidationError
from flask_admin import form


class PlotingForm(FlaskForm):
    x_points = wtforms.StringField(
        label="Puntos de X", validators=[validators.DataRequired()]
    )

    y_points = wtforms.StringField(
        label="Puntos de Y", validators=[validators.DataRequired()]
    )


class LoginForm(FlaskForm):
    username = wtforms.StringField(
        label="Usuario", validators=[validators.DataRequired(),]
    )

    password = wtforms.PasswordField(
        label="Contraseña", validators=[validators.DataRequired(),]
    )

    recordar = wtforms.BooleanField(label="recordarme?", default=False)

    def validate_password(self, field):
        user = User.query.filter(User.username == self.username.data).first()
        if user is None or not user.check_password(field.data):
            raise ValidationError("Usuario y/o contraseña invalido/s")


class RegistrationForm(FlaskForm):
    username = wtforms.StringField(
        label="Usuario",
        validators=[validators.DataRequired(), validators.Length(min=4, max=25)],
    )

    first_name = wtforms.StringField(label="Nombre")

    last_name = wtforms.StringField(label="Apellido")

    email = wtforms.StringField(
        label="correo electronico", validators=[validators.email("Email no valido")]
    )

    password1 = wtforms.PasswordField(
        label="Contraseña",
        validators=[
            validators.DataRequired(),
            validators.equal_to("password2", "Las contraseñas no coinciden"),
        ],
    )

    password2 = wtforms.PasswordField(
        label="Contraseña (confirmacion)", validators=[validators.DataRequired()]
    )


class EditProfileForm(FlaskForm):

    first_name = wtforms.StringField(label="Nombre")
    last_name = wtforms.StringField(label="Apellido")
    email = wtforms.StringField(
        label="correo electronico",
        validators=[
            validators.email("Correo no valido"),
            EmailUniqueness("Correo electronico ya registrado, ingrese otro"),
        ],
    )
    location = wtforms.StringField(label="location")
    gender = wtforms.SelectField(
        label="Genero",
        choices=[("nulo", "--"), ("hombre", "Hombre"), ("mujer", "Mujer")],
    )
    information = wtforms.TextAreaField(label="Informacion")
    avatar_file = file.FileField(
        validators=[
            file.FileAllowed(photos, "Archivo no valido, debe ser una imagen valida")
        ]
    )
