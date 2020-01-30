import os

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_user import UserManager

db = SQLAlchemy()


def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ['SECRET_KEY'],
        SQLALCHEMY_DATABASE_URI="".join(
            ["sqlite:///", app.instance_path, "/", "frogaday.sqlite"]
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        USER_APP_NAME="Frog.a.Day",
        USER_ENABLE_EMAIL=False,
        USER_ENABLE_USERNAME=True,
        USER_ENABLE_CHANGE_USERNAME=False,
        USER_REQUIRE_RETYPE_PASSWORD=True,
    )

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Setup the DB using SQLAlchemy
    db.init_app(app)

    with app.app_context():
        from .models import User
        from .models import Goal

        db.create_all()

    # Setup DB migrations
    migrate = Migrate(app, db)

    # Setup Flask-User and specify the User data-model
    user_manager = UserManager(app, db, User)

    # Setup application routes
    from . import main

    app.register_blueprint(main.bp)
    app.add_url_rule("/", endpoint="index")

    from . import sub

    app.register_blueprint(sub.bp)

    return app
