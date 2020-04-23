from flask_web_app import app, db
from flask_web_app.models import User, PostModel


@app.shell_context_processor
def make_shell_context():
    return {"db": db, "User": User, "PostModel": PostModel}


if __name__ == "__main__":
    app.run()
