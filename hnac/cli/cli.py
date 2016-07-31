import types
import os
from os import path

from flask_script import Manager

from hnac.crawlers import create_hackernews_api_crawler_job
from hnac.web.app import create_app
from hnac.configuration import default
from hnac.cli.commands.database import CreateDatabase
from hnac.cli.commands.users import (CreateAPIUser, ListAPIUsers,
                                     DeleteAPIUser, ChangeAPIUserPassword)


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

    user_manager = Manager(usage="API user management")
    user_manager.add_command("create", CreateAPIUser())
    user_manager.add_command("delete", DeleteAPIUser())
    user_manager.add_command("list", ListAPIUsers())
    user_manager.add_command("change_password", ChangeAPIUserPassword())

    manager.add_command("users", user_manager)

    manager.run()
