from unittest import TestCase, main

from mock import patch, Mock

from hnac.web.authentication import load_user
from hnac.models import User


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


if __name__ == "__main__":
    main()
