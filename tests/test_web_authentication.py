from unittest import main
from unittest.mock import patch, Mock

from hnac.web.authentication import (load_user, authenticate, identity,
                                     payload_handler)
from hnac.models import User
from hnac.web.database import db

from common import WebTestCaseWithUserAccount


def mocked_query():
    users = {
        1: User(id=1, username="user1", password="user1_password")
    }

    query_mock = Mock()
    query = query_mock.return_value
    query.get.side_effect = lambda user_id: users.get(user_id)

    return query_mock


class LoadUserTests(WebTestCaseWithUserAccount):
    @patch("hnac.web.database.db.session.query", mocked_query())
    def test_load_user(self):
        with self.app.app_context():
            user = load_user(1)

            self.assertIsNotNone(user)
            self.assertEqual(user.id, 1)
            self.assertEqual(user.username, self.test_user_username)


class Authenticatetests(WebTestCaseWithUserAccount):
    def test_authenticate(self):
        with self.app.app_context():
            user = authenticate(self.test_user_username,
                                self.test_user_password)

            self.assertIsNotNone(user)
            self.assertEqual(user.username, self.test_user_username)

    def test_fail_to_authenticate_unknown_user(self):
        with self.app.app_context():
            user = authenticate("user100", self.test_user_password)

            self.assertIsNone(user)

    def test_fail_to_authenticate_with_invalid_password(self):
        with self.app.app_context():
            user = authenticate(self.test_user_username, "invalid-password")

            self.assertIsNone(user)


class IdentityTests(WebTestCaseWithUserAccount):
    def test_identity(self):
        with self.app.app_context():
            user = User.get_by_username(db.session, self.test_user_username)

            payload = {
                "identity": user.id,
                "jti": user.jti
            }

            authenticated_user = identity(payload)

            self.assertIsNotNone(authenticated_user)
            self.assertEqual(authenticated_user.id, user.id)

    def test_fail_to_authenticate_with_invalid_user_id(self):
        with self.app.app_context():
            user = User.get_by_username(db.session, self.test_user_username)

            payload = {
                "identity": 12345,
                "jti": user.jti
            }

            authenticated_user = identity(payload)

            self.assertIsNone(authenticated_user)

    def test_fail_to_authenticate_with_invalid_jti(self):
        with self.app.app_context():
            user = User.get_by_username(db.session, self.test_user_username)

            payload = {
                "identity": user.id,
                "jti": "invalid-jti"
            }

            authenticated_user = identity(payload)

            self.assertIsNone(authenticated_user)


class PayloadHandlerTests(WebTestCaseWithUserAccount):
    def test_payload_handler(self):
        with self.app.app_context():
            user = User.get_by_username(db.session, self.test_user_username)

            payload = payload_handler(user)

            self.assertIsNotNone(payload)
            self.assertIsInstance(payload, dict)

            self.assertIn("identity", payload)
            self.assertIn("jti", payload)


if __name__ == "__main__":
    main()
