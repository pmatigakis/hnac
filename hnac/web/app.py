from sqlalchemy import create_engine
from flask import Flask

from hnac.web import SessionMaker, session
from hnac.web.apis.api_v1 import blueprint as api_v1
from hnac.web.views import frontend

def create_app(settings):
    engine = create_engine(settings.CONNECTION_STRING)

    SessionMaker.configure(bind=engine)

    app = Flask(__name__)

    app.debug = True

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        session.remove()

    app.register_blueprint(api_v1)
    app.register_blueprint(frontend)

    return app
