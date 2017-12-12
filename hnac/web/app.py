from sqlalchemy import create_engine
from flask import Flask
from flask_admin import Admin

from hnac.web import SessionMaker, session
from hnac.web.apis import api_v1
from hnac.web import views, jwt
from hnac.web.authentication import (login_manager, authenticate, identity,
                                     payload_handler)
from hnac.models import User, Report
from hnac.web.admin import (ReportModelView, UserModelView,
                            AuthenticatedIndexView)
from hnac.logging import configure_logging


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

    configure_logging(app.config)

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
    jwt.jwt_payload_callback = payload_handler

    jwt.init_app(app)

    admin = Admin(app, name="admin", template_mode='bootstrap3',
                  index_view=AuthenticatedIndexView())

    admin.add_view(UserModelView(User, session, endpoint="users"))
    admin.add_view(ReportModelView(Report, session, endpoint="reports"))

    app.register_blueprint(api_v1.blueprint, url_prefix="/api/v1")
    app.register_blueprint(views.blueprint)

    return app
