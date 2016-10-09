from unittest import main

from werkzeug.security import check_password_hash

from hnac.cli.commands.users import (CreateAPIUser, DeleteAPIUser,
                                     ChangeAPIUserPassword)
from hnac.web import session
from hnac.models import User

from common import CommandTestCase, CommandTestCaseWithMockData


class CreateAPIUserTests(CommandTestCase):
    def test_create_user(self):
        USERNAME = "user1"
        PASSWORD = "password"

        command = CreateAPIUser()

        command.run(USERNAME, PASSWORD)

        user = session.query(User).filter_by(username=USERNAME).one_or_none()

        self.assertIsNotNone(user)
        self.assertIsNotNone(user.id)
        self.assertEqual(user.username, USERNAME)
        self.assertTrue(check_password_hash(user.password, PASSWORD))


class DeleteAPIUserTests(CommandTestCaseWithMockData):
    def test_delete_user(self):
        command = DeleteAPIUser()

        command.run(self.test_user_username)

        user = session.query(User)\
                      .filter_by(username=self.test_user_username)\
                      .one_or_none()

        self.assertIsNone(user)


class ChangeAPIUserPasswordTests(CommandTestCaseWithMockData):
    def test_change_user_password(self):
        command = ChangeAPIUserPassword()

        new_password = "password2"

        command.run(self.test_user_username, new_password)

        user = session.query(User)\
                      .filter_by(username=self.test_user_username)\
                      .one_or_none()

        self.assertIsNotNone(user)
        self.assertIsNotNone(user.id)
        self.assertEqual(user.username, self.test_user_username)
        self.assertTrue(check_password_hash(user.password, new_password))


if __name__ == "__main__":
    main()
