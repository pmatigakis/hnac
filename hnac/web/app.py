from flask import Flask
from flask_admin import Admin

from hnac.web.database import db
from hnac.web.apis import api_v1
from hnac.web import views
from hnac.web.authentication import (
    login_manager, uauth, authentication_callback
)
from hnac.models import User, Report
from hnac.web.admin import (ReportModelView, UserModelView,
                            AuthenticatedIndexView)
from hnac.logging import configure_logging


def create_app():
    app = Flask(__name__)
    app.config.from_object("hnac.configuration.settings")

    configure_logging(app.config)

    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "frontend.login"

    uauth.init_app(app, authentication_callback)

    admin = Admin(app, name="admin", template_mode='bootstrap3',
                  index_view=AuthenticatedIndexView())

    admin.add_view(UserModelView(User, db.session, endpoint="users"))
    admin.add_view(ReportModelView(Report, db.session, endpoint="reports"))

    app.register_blueprint(api_v1.blueprint, url_prefix="/api/v1")
    app.register_blueprint(views.blueprint)

    return app
