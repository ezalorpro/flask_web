import json
import os
import re

import wtforms
from bokeh import plotting as plt
from bokeh.embed import components
from flask import jsonify, redirect, render_template, request, url_for, abort
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, login_url, login_user, logout_user
from PIL import Image, ImageOps
from sqlalchemy import func
from sqlalchemy.event import listens_for
from werkzeug.security import check_password_hash, generate_password_hash
from wtforms import validators

from flask_web_app import admin, app, db, file_path, login_manager, op, photos
from flask_web_app.forms import (CommentForm, EditProfileForm, LoginForm,
                                 PlotingForm, PostForm, RegistrationForm,
                                 SearchForm)
from flask_web_app.models import (CommentModel, ImagePostModel, PostModel,
                                  TagModel, User, genero)
from flask_web_app.utils import add_tags, login_required

EMAIL_REGX = r"[^@]+@[^@]+\.[^@]+"


@app.route("/", endpoint="home")
def home():
    posts = PostModel.query.order_by("post_date").all()[::-1]
    return render_template("home.html", posts=posts)


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(login_url("login", request.url))


@app.route("/logout", endpoint="logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/login", methods=["GET", "POST"], endpoint="login")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = LoginForm()
    if request.method == "POST":
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            login_user(user, remember=form.recordar.data)
            if request.form.get("next"):
                return redirect(request.form.get("next"))
            return redirect(url_for("home"))
        else:
            return render_template("login.html", form=form)
    else:
        return render_template("login.html", form=form)


@app.route("/registrar", methods=["GET", "POST"], endpoint="registrar")
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
            data = {"flag": bool(User.query.filter_by(username=data["name"]).first())}
        elif data["tipo"] == "email":
            if not bool(re.match(EMAIL_REGX, data["email"])):
                data = {
                    "flag": False,
                    "info": "Ingrese una dirección de correo electrónico válida.",
                }
            elif bool(User.query.filter_by(email=data["email"]).first()):
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


@app.route("/ploting", methods=["GET", "POST"], endpoint="ploting")
@login_required(role="regular_user")
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


@app.route("/profile", endpoint="profile")
@login_required(role="regular_user")
def profile():
    usuario = current_user
    post_object = (
        PostModel.query.filter_by(user=current_user).order_by("post_date").all()[::-1]
    )
    post_list = [item for item in post_object]
    return render_template(
        "profile.html", usuario=usuario, post_list=post_list, genero=genero
    )


@app.route("/edit_profile", methods=["GET", "POST"], endpoint="edit_profile")
@login_required(role="regular_user")
def edit_profile():
    perfilForm = EditProfileForm(obj=current_user)
    if request.method == "POST" and perfilForm.validate_on_submit():
        if request.files["avatar_file"]:
            profile_image_handler(
                current_user, perfilForm, request.files["avatar_file"].filename
            )
        perfilForm.populate_obj(current_user)
        db.session.commit()
        return redirect(url_for("profile"))
    else:
        return render_template(
            "edit_profile.html", perfilForm=perfilForm, usuario=current_user
        )


def profile_image_handler(user, form, filename):
    if user.avatar:
        try:
            os.remove(file_path + "/" + user.avatar)
            thumb_split = user.avatar.split(".")
            thumb_old = thumb_split[0] + "_thumb." + thumb_split[1]
            os.remove(file_path + "/" + thumb_old)
        except:
            pass

    fileUrl = user.username + "-" + filename
    photos.save(form.avatar_file.data, name=fileUrl)
    thumb = Image.open(file_path + "/" + fileUrl)
    thumb = ImageOps.fit(thumb.copy(), (50, 50), Image.ANTIALIAS)
    thumb_name = filename.split(".")
    with open(
        file_path
        + "/"
        + user.username
        + "-"
        + thumb_name[0]
        + "_thumb."
        + thumb_name[1],
        "wb",
    ) as fp:
        thumb.save(fp)
    user.avatar = fileUrl


@app.route("/posts", endpoint="list_posts")
@login_required(role=["admin", "editor"])
def list_posts():
    post_list = (
        PostModel.query.filter_by(user=current_user).order_by("post_date").all()[::-1]
    )
    return render_template("list_posts.html", post_list=post_list)


@app.route("/posts/<post_id>", endpoint="post_view")
def post_view(post_id):
    post = PostModel.query.get(post_id)
    form = CommentForm()
    comments = (
        CommentModel.query.filter_by(post_id=post.id).order_by("comment_date").all()
    )
    return render_template(
        "post_template.html", post=post, form=form, comments=comments
    )


@app.route("/comment_post/<post_id>", methods=["POST"], endpoint="comment_post")
@login_required(role="regular_user")
def comment_post(post_id):
    form = CommentForm()
    if form.validate_on_submit():
        comment = CommentModel(user=current_user)
        form.populate_obj(comment)
        post = PostModel.query.get(post_id)
        post.comments.append(comment)
        db.session.commit()
        return redirect(url_for("post_view", post_id=post_id))


@app.route("/edit_comment/<comment_id>", methods=["POST"], endpoint="edit_comment")
@login_required(role="regular_user")
def edit_comment(comment_id):
    comment = CommentModel.query.get(comment_id)
    if current_user == comment.user:
        comment.comment_text = request.form["com_" + str(comment.id)]
        db.session.commit()
        return redirect(url_for("post_view", post_id=comment.post_id))
    else:
        return abort("404")
        

@app.route('/delete_comment/<comment_id>', methods=['POST'], endpoint="delete_comment")
@login_required(role="regular_user")
def delete_comment(comment_id):
    comment = CommentModel.query.get(comment_id)
    if current_user == comment.user:
        post_id = comment.post_id
        db.session.delete(comment)
        db.session.commit()
        return redirect(url_for("post_view", post_id=post_id))
    else:
        return abort("404")
    
@app.route("/delete_post/<id>", methods=["GET", "POST"], endpoint="delete_post")
@login_required(role=["admin", "editor"])
def delete_post(id):
    if request.method == "POST":
        post = PostModel.query.get(id)
        if post.user == current_user or current_user.role == "admin":
            db.session.delete(post)
            db.session.commit()
            return redirect(url_for("profile"))
        else:
            return redirect(url_for("home"))
    else:
        return redirect(url_for("home"))


@app.route("/create_post", methods=["GET", "POST"], endpoint="create_post")
@login_required(role=["admin", "editor"])
def create_post():
    post_form = PostForm()
    post_form.post_id = None
    if request.method == "POST" and post_form.validate_on_submit():
        post = PostModel()
        post_form.populate_obj(post)
        tags_list = [val.strip() for val in post_form.tags_form.data.split(",")]
        tag_acum = []
        for tag in tags_list:
            if tag:
                tag_acum.append(add_tags(tag))
        post.tags = tag_acum
        post.user = current_user
        db.session.add(post)
        db.session.flush()
        manage_images(post)
        db.session.commit()
        return redirect(url_for("post_view", post_id=post.id))
    else:
        tags_obj = TagModel.query.all()
        tags = json.dumps({k.name: None for k in tags_obj})
        current_tags = {}
        return render_template(
            "create_post.html",
            post_form=post_form,
            tags=tags,
            current_tags=current_tags,
        )


@app.route("/edit_post/<post_id>", methods=["GET", "POST"], endpoint="edit_post")
@login_required(role=["admin", "editor"])
def edit_post(post_id):
    post = PostModel.query.get(post_id)

    if post.user != current_user and current_user.role not in ["admin"]:
        return redirect(url_for("home"))

    post_form = PostForm(obj=post)
    post_form.post_id = post_id
    if request.method == "POST" and post_form.validate_on_submit():
        post_form.populate_obj(post)
        tags_list = [val.strip() for val in post_form.tags_form.data.split(",")]
        tag_acum = []
        for tag in tags_list:
            if tag:
                tag_acum.append(add_tags(tag))
        post.tags = tag_acum
        db.session.flush()
        manage_images(post)
        db.session.commit()
        return redirect(url_for("post_view", post_id=post.id))
    else:
        tags_obj = TagModel.query.all()
        tags = json.dumps({k.name: None for k in tags_obj})
        current_tags = [{"tag": tag.name} for tag in post.tags]
        return render_template(
            "create_post.html",
            post_form=post_form,
            post=post,
            tags=tags,
            current_tags=current_tags,
        )


@login_required(role=["admin", "editor"])
def manage_images(post):
    images1 = ImagePostModel.query.filter_by(post=None).all()
    if images1:
        for image in images1:
            if image.path in post.post_text:
                image.post = post
            elif image.user == post.user:
                db.session.delete(image)

    images2 = ImagePostModel.query.filter_by(post=post).all()
    if images2:
        for image in images2:
            if image.path not in post.post_text:
                db.session.delete(image)


@app.route("/clean_data_post", methods=["GET", "POST"], endpoint="clean_data_post")
@login_required(role=["admin", "editor"])
def clean_data_post():
    images = ImagePostModel.query.filter_by(post=None).all()
    if images:
        for image in images:
            db.session.delete(image)
    db.session.commit()
    return redirect(url_for("profile"))


@app.route("/post_image_handler", methods=["POST"], endpoint="post_image_handler")
def post_image_handler():
    image = request.files["file"]
    image_name = request.files["file"].filename
    image_db = ImagePostModel(user=current_user)
    db.session.add(image_db)
    db.session.flush()
    image_db.path = str(image_db.id) + "-" + image_name
    image_name = image_db.path
    db.session.commit()
    photos.save(image, name=image_name)
    return jsonify({"location": url_for("static", filename="images/" + image_name)})


@app.route("/search/", methods=["GET", "POST"])
@app.route("/search/<query_type>/<query>", methods=["GET", "POST"])
def search(query_type=None, query=None):
    form = SearchForm()
    if request.method == "POST" and form.validate_on_submit():
        query = request.form["busqueda"]
        tipo = request.form["tipo"]
        if tipo == "title":
            results = (
                db.session.query(PostModel)
                .filter(func.lower(PostModel.title).contains(query.lower()))
                .order_by(PostModel.post_date)
                .all()[::-1]
            )
        elif tipo == "author":
            results = (
                db.session.query(PostModel)
                .filter(PostModel.user.has(func.lower(User.username).contains(query.lower())))
                .order_by(PostModel.post_date)
                .all()[::-1]
            )
        elif tipo == "tag":
            results = (
                db.session.query(PostModel)
                .filter(PostModel.tags.any(func.lower(TagModel.name).contains(query.lower())))
                .order_by(PostModel.post_date)
                .all()[::-1]
            )
        return render_template("search.html", form=form, results=results)
    elif query:
        if query_type == "tag":
            results = (
                db.session.query(PostModel)
                .filter(PostModel.tags.any(func.lower(TagModel.name).contains(query.lower())))
                .order_by(PostModel.post_date)
                .all()[::-1]
            )
        if query_type == "home":
            query = request.args["search"]
            results = (
                db.session.query(PostModel)
                .filter(func.lower(PostModel.title).contains(query.lower()))
                .order_by(PostModel.post_date)
                .all()[::-1]
            )
        form.busqueda.data = query
        form.tipo.data = query_type
        return render_template("search.html", form=form, results=results)
    else:
        print(form.busqueda)
        return render_template("search.html", form=form)


@listens_for(PostModel, "before_delete")
def del_post_model(mapper, connection, target):
    images = ImagePostModel.query.filter_by(post=target).all()
    if images:
        for image in images:
            try:
                os.remove(op.join(file_path, image.path))
            except OSError:
                pass


@listens_for(ImagePostModel, "before_delete")
def del_image_post_model(mapper, connection, target):
    if target.path:
        try:
            os.remove(op.join(file_path, target.path))
        except OSError:
            pass
