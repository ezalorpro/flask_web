import json
import re

import wtforms
from bokeh import plotting as plt
from bokeh.embed import components
from flask import jsonify, redirect, render_template, request, url_for
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, login_required, login_url, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from wtforms import validators

from flask_web_app import admin, app, db, login_manager, photos
from flask_web_app.forms import LoginForm, PlotingForm, RegistrationForm, EditProfileForm
from flask_web_app.models import User, PostModel

EMAIL_REGX = r"[^@]+@[^@]+\.[^@]+"


@app.route("/")
def home():
    return render_template("home.html")


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(login_url("login", request.url))


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = LoginForm()
    if request.method == "POST":
        if form.validate_on_submit():
            user = User.query.filter(User.username == form.username.data).first()
            login_user(user, remember=form.recordar.data)
            if request.form.get("next"):
                return redirect(request.form.get("next"))
            return redirect(url_for("home"))
        else:
            return render_template("login.html", form=form)
    else:
        return render_template("login.html", form=form)


@app.route("/registrar", methods=["GET", "POST"])
def registrar():
    form = RegistrationForm()
    data = request.args
    if request.method == "POST" and form.validate_on_submit():
        user = User()
        form.populate_obj(user)
        user.set_password(form.password1.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login"))
    elif data:
        if data["tipo"] == "username":
            data = {
                "flag": bool(User.query.filter(User.username == data["name"]).first())
            }
        elif data["tipo"] == "email":
            if not bool(re.match(EMAIL_REGX, data["email"])):
                data = {
                    "flag": False,
                    "info": "Ingrese una dirección de correo electrónico válida.",
                }
            elif bool(User.query.filter(User.email == data["email"]).first()):
                data = {
                    "flag": False,
                    "info": "Correo electronico ya registrado, ingrese otro",
                }
            else:
                data = {
                    "flag": True,
                    "info": "",
                }

        return jsonify(data)
    else:
        return render_template("registrar.html", form=form)


@app.route("/ploting", methods=["GET", "POST"])
@login_required
def ploting():
    if request.method == "POST":
        x_data = json.loads(request.form["x_points"])
        y_data = json.loads(request.form["y_points"])

        p = plt.figure(sizing_mode="scale_width")
        p.line(x_data, y_data)

        script_bok, div_bok = components(p)
        return script_bok + div_bok
    else:
        form = PlotingForm()
        x_data = [0]
        y_data = [0]

        p = plt.figure(sizing_mode="scale_width")
        p.line(x_data, y_data)
        script_bok, div_bok = components(p)
        context = {"form": form, "div_bok": div_bok, "script_bok": script_bok}
        return render_template("ploting.html", **context)


@app.route('/posts')
@login_required
def list_posts():
    post_object = PostModel.query.filter(PostModel.user == current_user).all()
    post_list = [item for item in post_object]
    return render_template('list_posts.html', post_list=post_list)


@app.route('/posts/<post_id>')
@login_required
def post_view(post_id):
    post = PostModel.query.filter(PostModel.id == post_id).first()
    print(post.user)
    return render_template('post_template.html', post=post)


@app.route('/profile')
@login_required
def profile():
    usuario = current_user
    post_object = PostModel.query.filter(PostModel.user == current_user).all()
    post_list = [item for item in post_object]
    return render_template('profile.html', usuario=usuario, post_list=post_list)

@app.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    perfilForm = EditProfileForm(obj=current_user)
    if request.method == 'POST' and perfilForm.validate_on_submit():
        fileUrl = current_user.username + request.files['avatar_file'].filename
        filename = photos.save(perfilForm.avatar_file.data)
        perfilForm.populate_obj(current_user)
        current_user.avatar = fileUrl
        db.session.commit()
        return redirect('plots:profile')
    else:
        return render_template('edit_profile.html', perfilForm=perfilForm, usuario=current_user)
