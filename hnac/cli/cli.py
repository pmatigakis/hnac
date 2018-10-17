import os
from os import path

from flask_script import Manager

from hnac.web.app import create_app
from hnac.cli.commands.users import (CreateAPIUser, ListAPIUsers,
                                     DeleteAPIUser, ChangeAPIUserPassword)
from hnac.cli.commands.crawler import Crawl
from hnac.cli.commands.tokens import (
    CreateToken, DeleteToken, GetToken, ListTRokens
)
from hnac.cli.commands.stories import DumpStories


def main():
    configuration_file_path = path.abspath("settings.py")

    if not path.exists(configuration_file_path):
        print("File settings.py doesn't exist")
        exit(1)
    elif not path.isfile(configuration_file_path):
        print("settings.py is not a file")
        exit(1)

    environment = os.environ.get("ENVIRONMENT", "production")

    app = create_app(environment, configuration_file_path)

    manager = Manager(app)

    user_manager = Manager(usage="API user management")
    user_manager.add_command("create", CreateAPIUser())
    user_manager.add_command("delete", DeleteAPIUser())
    user_manager.add_command("list", ListAPIUsers())
    user_manager.add_command("change_password", ChangeAPIUserPassword())

    manager.add_command("users", user_manager)

    manager.add_command("crawl", Crawl())

    token_manager = Manager(usage="API token management")
    token_manager.add_command("create", CreateToken())
    token_manager.add_command("list", ListTRokens())
    token_manager.add_command("get", GetToken())
    token_manager.add_command("delete", DeleteToken())
    manager.add_command("tokens", token_manager)

    stories_manager = Manager(usage="Story management commands")
    stories_manager.add_command("dump", DumpStories())
    manager.add_command("stories", stories_manager)

    manager.run()
