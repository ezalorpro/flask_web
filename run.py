from flask_web_app import app, db
from flask_web_app.models import (CommentModel, ImagePostModel, PostModel,
                                  TagModel, User)


@app.shell_context_processor
def make_shell_context():
    return {
        "db": db,
        "User": User,
        "PostModel": PostModel,
        "ImagePostModel": ImagePostModel,
        "TagModel": TagModel,
        "CommentModel": CommentModel,
    }


if __name__ == "__main__":
    app.run()
