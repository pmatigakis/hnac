from flask_script import Command, Option

from hnac.models import User
from hnac.web.database import db


class CreateAPIUser(Command):
    """Create a new API user"""

    option_list = (
        Option("username"),
        Option("password"),
    )

    def run(self, username, password):
        user = User.get_by_username(db.session, username)

        if user:
            print("User '{}' already exists".format(username))

            return

        user = User.create(db.session, username, password)

        db.session.commit()

        print("Added user {}".format(user.username))


class DeleteAPIUser(Command):
    """Delete an API user"""

    option_list = (
        Option("username"),
    )

    def run(self, username):
        user = User.delete(db.session, username)

        if not user:
            print("User {} doesn't exist".format(username))
            return

        db.session.commit()

        print("Removed user {}".format(username))


class ListAPIUsers(Command):
    """List the API users"""

    def run(self):
        print("Username\t\tRegistered at")
        for user in db.session.query(User).all():
            msg = "{username}\t\t{registered_at}"
            print(msg.format(username=user.username,
                             registered_at=user.registered_at))


class ChangeAPIUserPassword(Command):
    """Change a user's password"""

    option_list = (
        Option("username"),
        Option("password"),
    )

    def run(self, username, password):
        user = User.get_by_username(db.session, username)

        if not user:
            print("User {} doesn't exist".format(username))
            return

        user.change_password(password)

        db.session.commit()

        print("Change password for user '{}'".format(user.username))
