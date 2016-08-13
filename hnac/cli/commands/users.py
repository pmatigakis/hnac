from flask_script import Command, Option

from hnac.models import User
from hnac.web import session


class CreateAPIUser(Command):
    """Create a new API user"""

    option_list = (
        Option("username"),
        Option("password"),
    )

    def run(self, username, password):
        user = User.get_by_username(session, username)

        if user:
            print("User '{}' already exists".format(username))

            return

        user = User.create(session, username, password)

        session.commit()

        print("Added user {}".format(user.username))


class DeleteAPIUser(Command):
    """Delete an API user"""

    option_list = (
        Option("username"),
    )

    def run(self, username):
        user = User.delete(session, username)

        if not user:
            print("User {} doesn't exist".format(username))
            return

        session.commit()

        print("Removed user {}".format(username))


class ListAPIUsers(Command):
    """List the API users"""

    def run(self):
        print("Username\t\tRegistered at")
        for user in session.query(User).all():
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
        user = User.get_by_username(session, username)

        if not user:
            print("User {} doesn't exist".format(username))
            return

        user.change_password(password)

        session.commit()

        print("Change password for user '{}'".format(user.username))
