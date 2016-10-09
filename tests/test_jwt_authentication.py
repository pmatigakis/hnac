from unittest import TestCase, main
from os.path import join, dirname, abspath
import json

from sqlalchemy import create_engine

from hnac.models import User, Base
from hnac.web.app import create_app
from hnac.web import session

from mock_data import load_mock_data
from common import WebTestCaseWithUserAccount


class JWTAuthenticationTests(WebTestCaseWithUserAccount):
    def test_authenticate_with_jwt(self):
        headers = {
            "Content-Type": "application/json"
        }

        data = json.dumps({"username": self.test_user_username, "password": self.test_user_password})

        response = self.client.post("/auth", data=data, headers=headers)

        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.data)

        self.assertIn("access_token", response_data)

    def test_fail_to_authenticate_with_jwt_using_invalid_password(self):
        headers = {
            "Content-Type": "application/json"
        }

        data = json.dumps({"username": self.test_user_username, "password": "invalid-pass"})

        response = self.client.post("/auth", data=data, headers=headers)

        self.assertEqual(response.status_code, 401)

        response_data = json.loads(response.data)

        expected_response = {
            u'status_code': 401,
            u'description': u'Invalid credentials',
            u'error': u'Bad Request'
        }

        self.assertDictEqual(response_data, expected_response)

    def test_fail_to_authenticate_with_jwt_using_unknown_username(self):
        headers = {
            "Content-Type": "application/json"
        }

        data = json.dumps({"username": "user100", "password": self.test_user_password})

        response = self.client.post("/auth", data=data, headers=headers)

        self.assertEqual(response.status_code, 401)

        response_data = json.loads(response.data)

        expected_response = {
            u'status_code': 401,
            u'description': u'Invalid credentials',
            u'error': u'Bad Request'
        }

        self.assertDictEqual(response_data, expected_response)


class ProtectedAPIEndpointAccessTests(WebTestCaseWithUserAccount):
    def test_access_protected_endpoint(self):
        token = self.authenticate_using_jwt(self.test_user_username, self.test_user_password)

        client = self.app.test_client()

        headers = {
            "Authorization": "JWT {}".format(token)
        }

        response = client.get("/api/v1/stories", headers=headers)

        self.assertEqual(response.status_code, 200)

    def test_fail_to_access_protected_endpoint_with_invalidated_token(self):
        token = self.authenticate_using_jwt(self.test_user_username, self.test_user_password)

        with self.app.app_context():
            user = User.get_by_username(session, "user1")
            user.reset_token_identifier()
            try:
                session.commit()
            except Exception:
                session.rollback()
                self.fail("Failed to reset the user jti")

        headers = {
            "Authorization": "JWT {}".format(token)
        }

        response = self.client.get("/api/v1/stories", headers=headers)

        self.assertEqual(response.status_code, 401)

        response_data = json.loads(response.data)

        expected_response = {
            u'description': u'User does not exist',
            u'error': u'Invalid JWT',
            u'status_code': 401
        }

        self.assertDictEqual(response_data, expected_response)


if __name__ == "__main__":
    main()
