from flask import Flask
from flask_mail import Mail
import logging
import os

from . import database as db_handler


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="Umamusume",
        DB_NAME="stk_addons_next",
        DB_HOST=None,
        DB_PORT=None,
        DB_USER=None,
        DB_PASS=None,
        DB_PASSWORD=None,
        VERSION="0.1 - Special Week",
    )
    app.config.from_pyfile("config.py", True)
    os.makedirs(app.instance_path, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        style="{",
        datefmt="%Y-%m-%d %H:%M:%S",
        format="{asctime} {levelname} {name}: {message} [{pathname}:{lineno}]",
    )

    mail = Mail()

    mail.init_app(app)
    db_handler.init_app(app)

    from .api import bp as api
    from .resources import bp as resources
    from .routes.index import bp as index
    from .routes.register import bp as register

    app.register_blueprint(api)
    app.register_blueprint(resources)
    app.register_blueprint(index)
    app.register_blueprint(register)

    return app
