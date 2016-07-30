import types
import os
from os import path

from sqlalchemy import create_engine

from hnac.crawlers import create_hackernews_api_crawler_job
from hnac.web.app import create_app
from hnac.models import Base
from hnac.configuration import default


def start_crawler():
    configuration_file_path = path.abspath("settings.py")

    if not path.exists(configuration_file_path):
        print("File settings.py doesn't exist")
        exit(1)
    elif not path.isfile(configuration_file_path):
        print("settings.py is not a file")
        exit(1)

    config = default.__dict__.copy()

    d = types.ModuleType('settings')
    d.__file__ = configuration_file_path

    with open(configuration_file_path) as config_file:
        exec(compile(config_file.read(), configuration_file_path, 'exec'),
             d.__dict__)

    for item in d.__dict__:
        config[item] = d.__dict__[item]

    job = create_hackernews_api_crawler_job(config)

    job.run()


def start_api_server():
    configuration_file_path = path.abspath("settings.py")

    if not path.exists(configuration_file_path):
        print("File settings.py doesn't exist")
        exit(1)
    elif not path.isfile(configuration_file_path):
        print("settings.py is not a file")
        exit(1)

    environment = os.environ.get("HNAC_API_ENVIRONMENT", "production")

    app = create_app(environment, configuration_file_path)

    host = app.config["HNAC_API_HOST"]
    port = app.config["HNAC_API_PORT"]

    app.run(host, port)


def create_database():
    configuration_file_path = path.abspath("settings.py")

    if not path.exists(configuration_file_path):
        print("File settings.py doesn't exist")
        exit(1)
    elif not path.isfile(configuration_file_path):
        print("settings.py is not a file")
        exit(1)

    d = types.ModuleType('settings')
    d.__file__ = configuration_file_path

    with open(configuration_file_path) as config_file:
        exec(compile(config_file.read(), configuration_file_path, 'exec'),
             d.__dict__)

    if "HNAC_DB" not in d.__dict__:
        print("The settings variable HNAC_DB does't exist")
        exit(1)

    engine = create_engine(d.HNAC_DB)

    Base.metadata.create_all(engine)
