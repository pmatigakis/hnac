import types
import os
from os import path

from sqlalchemy import create_engine
from flask.ext.script import Manager, Command
from flask import current_app

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


class CreateDatabase(Command):
    """Create the hackernews crawler database"""

    def run(self):
        config = current_app.config

        engine = create_engine(config["HNAC_DB"])
        Base.metadata.create_all(engine)


def main():
    configuration_file_path = path.abspath("settings.py")

    if not path.exists(configuration_file_path):
        print("File settings.py doesn't exist")
        exit(1)
    elif not path.isfile(configuration_file_path):
        print("settings.py is not a file")
        exit(1)

    environment = os.environ.get("HNAC_API_ENVIRONMENT", "production")

    app = create_app(environment, configuration_file_path)

    manager = Manager(app)

    manager.add_command("initdb", CreateDatabase())

    manager.run()
