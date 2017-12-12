from logging.config import dictConfig


def configure_logging(config):
    if "LOGGING" in config:
        dictConfig(config["LOGGING"])
