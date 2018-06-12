from unittest import main
from unittest.mock import patch, Mock

from hnac.web.authentication import load_user, authentication_callback
from hnac.models import User

from common import WebTestCaseWithUserAccount, ModelTestCaseWithMockData


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


class AuthenticationCallbackTests(ModelTestCaseWithMockData):
    def test_get_token_using_callback(self):
        with self.app.app_context():
            token = authentication_callback(self.test_token)
            self.assertIsNotNone(token)
            self.assertEqual(token.value, self.test_token)


if __name__ == "__main__":
    main()
