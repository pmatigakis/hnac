from datetime import datetime
from os.path import abspath, dirname, join
from unittest import TestCase, main

from werkzeug.security import check_password_hash
from sqlalchemy import create_engine

from hnac.cli.commands.users import (CreateAPIUser, DeleteAPIUser,
                                     ChangeAPIUserPassword)
from hnac.web.app import create_app
from hnac.web import session
from hnac.models import User, Base


class CreateAPIUserTests(TestCase):
    def setUp(self):
        settings_path = join(dirname(abspath(__file__)), "settings.py")
        self.app = create_app("testing", settings_path)

        engine = create_engine("sqlite:///test.db")
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

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


class DeleteAPIUserTests(TestCase):
    def setUp(self):
        settings_path = join(dirname(abspath(__file__)), "settings.py")
        self.app = create_app("testing", settings_path)

        engine = create_engine("sqlite:///test.db")
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

        self.username = "user1"
        self.password = "password"

        user = User(username=self.username, password=self.password,
                    registered_at=datetime.utcnow(), active=True)

        session.add(user)
        session.commit()

    def test_delete_user(self):
        command = DeleteAPIUser()

        command.run(self.username)

        user = session.query(User)\
                      .filter_by(username=self.username)\
                      .one_or_none()

        self.assertIsNone(user)


class ChangeAPIUserPasswordTests(TestCase):
    def setUp(self):
        settings_path = join(dirname(abspath(__file__)), "settings.py")
        self.app = create_app("testing", settings_path)

        engine = create_engine("sqlite:///test.db")
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

        self.username = "user1"
        self.password = "password"

        user = User(username=self.username, password=self.password,
                    registered_at=datetime.utcnow(), active=True)
        session.add(user)
        session.commit()

    def test_change_user_password(self):
        command = ChangeAPIUserPassword()

        new_password = "password2"

        command.run(self.username, new_password)

        user = session.query(User)\
                      .filter_by(username=self.username)\
                      .one_or_none()

        self.assertIsNotNone(user)
        self.assertIsNotNone(user.id)
        self.assertEqual(user.username, self.username)
        self.assertTrue(check_password_hash(user.password, new_password))


if __name__ == "__main__":
    main()
