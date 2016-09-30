from unittest import TestCase, main
from os.path import join, dirname, abspath

from mock import patch, Mock
from sqlalchemy import create_engine

from hnac.web.authentication import (load_user, authenticate, identity,
                                     payload_handler)
from hnac.models import User, Base
from hnac.web.app import create_app
from hnac.web import session

from mock_data import load_mock_data


def mocked_query():
    users = {
        1: User(id=1, username="user1", password="user1_password")
    }

    query_mock = Mock()
    query = query_mock.return_value
    query.get.side_effect = lambda user_id: users.get(user_id)

    return query_mock


class LoadUserTests(TestCase):
    @patch("hnac.web.session.query", mocked_query())
    def test_load_user(self):
        user = load_user(1)

        self.assertIsNotNone(user)
        self.assertEqual(user.id, 1)
        self.assertEqual(user.username, "user1")
        self.assertEqual(user.password, "user1_password")


class Authenticatetests(TestCase):
    def setUp(self):
        engine = create_engine("sqlite:///test.db")
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

        settings_path = join(dirname(abspath(__file__)), "settings.py")
        self.app = create_app("testing", settings_path)

        load_mock_data(session)

        try:
            session.commit()
        except:
            session.rollback()
            self.fail("Failed to load mock data")

    def tearDown(self):
        session.remove()

    def test_authenticate(self):
        user = authenticate("user1", "user1password")

        self.assertIsNotNone(user)
        self.assertEqual(user.username, "user1")

    def test_fail_to_authenticate_unknown_user(self):
        user = authenticate("user100", "user100password")

        self.assertIsNone(user)

    def test_fail_to_authenticate_with_invalid_password(self):
        user = authenticate("user1", "invalid-password")

        self.assertIsNone(user)


class IdentityTests(TestCase):
    def setUp(self):
        engine = create_engine("sqlite:///test.db")
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

        settings_path = join(dirname(abspath(__file__)), "settings.py")
        self.app = create_app("testing", settings_path)

        load_mock_data(session)

        try:
            session.commit()
        except:
            session.rollback()
            self.fail("Failed to load mock data")

    def tearDown(self):
        session.remove()

    def test_identity(self):
        user = User.get_by_username(session, "user1")

        payload = {
            "identity": user.id,
            "jti": user.jti
        }

        authenticated_user = identity(payload)

        self.assertIsNotNone(authenticated_user)
        self.assertEqual(authenticated_user.id, user.id)

    def test_fail_to_authenticate_with_invalid_user_id(self):
        user = User.get_by_username(session, "user1")

        payload = {
            "identity": 12345,
            "jti": user.jti
        }

        authenticated_user = identity(payload)

        self.assertIsNone(authenticated_user)

    def test_fail_to_authenticate_with_invalid_jti(self):
        user = User.get_by_username(session, "user1")

        payload = {
            "identity": user.id,
            "jti": "invalid-jti"
        }

        authenticated_user = identity(payload)

        self.assertIsNone(authenticated_user)


class PayloadHandlerTests(TestCase):
    def setUp(self):
        engine = create_engine("sqlite:///test.db")
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

        settings_path = join(dirname(abspath(__file__)), "settings.py")
        self.app = create_app("testing", settings_path)

        load_mock_data(session)

        try:
            session.commit()
        except:
            session.rollback()
            self.fail("Failed to load mock data")

    def tearDown(self):
        session.remove()

    def test_payload_handler(self):
        user = User.get_by_username(session, "user1")

        with self.app.app_context():
            payload = payload_handler(user)

            self.assertIsNotNone(payload)
            self.assertIsInstance(payload, dict)

            self.assertIn("identity", payload)
            self.assertIn("jti", payload)


if __name__ == "__main__":
    main()
