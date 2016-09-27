import logging
from logging.handlers import RotatingFileHandler
from sqlalchemy import create_engine
from flask import Flask

from hnac.web import SessionMaker, session
from hnac.web.apis import api_v1
from hnac.web import views, jwt
from hnac.web.authentication import login_manager, authenticate, identity


def create_app(environment="production", settings_module=None):
    app = Flask(__name__)

    configuration_modules = {
        "production": "hnac.configuration.production",
        "development": "hnac.configuration.development",
        "testing": "hnac.configuration.testing"
    }

    app.config.from_object("hnac.configuration.default")
    app.config.from_object(configuration_modules[environment])

    if settings_module:
        app.config.from_pyfile(settings_module)

    if app.config["API_ENABLE_LOGGING"]:
        log_level = app.config["API_LOG_LEVEL"]

        log_format = app.config["API_LOG_FORMAT"]

        formatter = logging.Formatter(log_format)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(log_level)

        app.logger.addHandler(console_handler)

        log_file = app.config["API_LOG_FILE"]

        file_handler = RotatingFileHandler(
            log_file,
            mode="a",
            maxBytes=app.config["API_LOG_FILE_SIZE"],
            backupCount=app.config["API_LOG_FILE_COUNT"]
        )

        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)

        app.logger.addHandler(file_handler)

        app.logger.setLevel(log_level)

    db = app.config["DB"]

    engine = create_engine(db)

    SessionMaker.configure(bind=engine)

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        session.remove()

    login_manager.init_app(app)
    login_manager.login_view = "frontend.login"

    jwt.authentication_callback = authenticate
    jwt.identity_callback = identity
    jwt.init_app(app)

    app.register_blueprint(api_v1.blueprint, url_prefix="/api/v1")
    app.register_blueprint(views.blueprint)

    return app
