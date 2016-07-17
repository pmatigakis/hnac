import logging
from logging.handlers import RotatingFileHandler
from sqlalchemy import create_engine
from flask import Flask

from hnac.web import SessionMaker, session
from hnac.web.apis.api_v1 import blueprint as api_v1
from hnac.web.views import frontend
from hnac.configuration import (HNAC_DB_SECTION, HNAC_DB, HNAC_API_SECTION,
                                HNAC_API_ENABLE_LOGGING, HNAC_API_LOG_FILE,
                                HNAC_API_LOG_DEBUG_LEVEL,
                                DEFAULT_API_LOG_FILENAME,
                                HNAC_API_LOG_FILE_SIZE,
                                HNAC_API_LOG_FILE_COUNT)


def create_app(config):
    app = Flask(__name__)

    if config.get(HNAC_API_SECTION, HNAC_API_ENABLE_LOGGING):
        log_level = logging.INFO
        
        if config.getboolean(HNAC_API_SECTION, HNAC_API_LOG_DEBUG_LEVEL):
            log_level = logging.DEBUG

        log_format = "%(asctime)s %(name)s %(levelname)s %(message)s"

        formatter = logging.Formatter(log_format)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(log_level)

        app.logger.addHandler(console_handler)

        log_file = (config.get(HNAC_API_SECTION, HNAC_API_LOG_FILE)
                    or DEFAULT_API_LOG_FILENAME)

        file_handler = RotatingFileHandler(
            log_file,
            mode="a",
            maxBytes=config.getint(HNAC_API_SECTION,
                                   HNAC_API_LOG_FILE_SIZE),
            backupCount=config.getint(HNAC_API_SECTION,
                                      HNAC_API_LOG_FILE_COUNT)
        )

        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)

        app.logger.addHandler(file_handler)

        app.logger.setLevel(log_level)

    db = config.get(HNAC_DB_SECTION, HNAC_DB)

    engine = create_engine(db)

    app.logger.debug("this is a debug message")
    app.logger.error("this is a error message")
    app.logger.info("this is a info message")

    SessionMaker.configure(bind=engine)

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        session.remove()

    app.register_blueprint(api_v1)
    app.register_blueprint(frontend)

    return app
