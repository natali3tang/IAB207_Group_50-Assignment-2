# from package import Class
from flask import Flask, app, render_template
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

db = SQLAlchemy()


# create a function that creates a web application
# a web server will run this web application
def create_app():
    app = Flask(
        __name__
    )  # this is the name of the module/package that is calling this app

    Bcrypt(app)

    app.debug = True
    app.secret_key = "supersecretKey123"
    # set the app configuration data
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///changemakers.sqlite"
    # initialise db with flask app
    db.init_app(app)

    bootstrap = Bootstrap5(app)

    # config upload folder
    UPLOAD_FOLDER = "/static/img"
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    app.config["STATIC_FOLDER"] = "static"

    # initialize the login manager
    login_manager = LoginManager()

    # set the name of the login function that lets user login
    # in our case it is auth.login (blueprintname.viewfunction name)
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    # create a user loader function takes userid and returns User
    from .models import User  # importing here to avoid circular references

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.errorhandler(404)
    # inbuilt function which takes error as parameter
    def not_found(e):
        return render_template("404.html", error=e), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        # note that we set the 500 status explicitly
        return render_template("500.html", error=e), 500

    # importing views module here to avoid circular references
    from . import views

    app.register_blueprint(views.bp)

    from . import auth

    app.register_blueprint(auth.bp)

    from . import events

    app.register_blueprint(events.bp)

    return app
