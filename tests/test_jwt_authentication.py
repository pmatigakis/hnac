from unittest import TestCase, main
from os.path import join, dirname, abspath
import json

from sqlalchemy import create_engine

from hnac.models import User, Base
from hnac.web.app import create_app
from hnac.web import session

from mock_data import load_mock_data


class JWTAuthenticationTests(TestCase):
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

    def test_authenticate_with_jwt(self):
        client = self.app.test_client()

        headers = {
            "Content-Type": "application/json"
        }

        data = json.dumps({"username": "user1", "password": "user1password"})

        response = client.post("/auth", data=data, headers=headers)

        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.data)

        self.assertIn("access_token", response_data)

    def test_fail_to_authenticate_with_jwt_using_invalid_password(self):
        client = self.app.test_client()

        headers = {
            "Content-Type": "application/json"
        }

        data = json.dumps({"username": "user1", "password": "invalid-pass"})

        response = client.post("/auth", data=data, headers=headers)

        self.assertEqual(response.status_code, 401)

        response_data = json.loads(response.data)

        expected_response = {
            u'status_code': 401,
            u'description': u'Invalid credentials',
            u'error': u'Bad Request'
        }

        self.assertDictEqual(response_data, expected_response)

    def test_fail_to_authenticate_with_jwt_using_unknown_username(self):
        client = self.app.test_client()

        headers = {
            "Content-Type": "application/json"
        }

        data = json.dumps({"username": "user100", "password": "user1password"})

        response = client.post("/auth", data=data, headers=headers)

        self.assertEqual(response.status_code, 401)

        response_data = json.loads(response.data)

        expected_response = {
            u'status_code': 401,
            u'description': u'Invalid credentials',
            u'error': u'Bad Request'
        }

        self.assertDictEqual(response_data, expected_response)


class ProtectedAPIEndpointAccessTests(TestCase):
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

    def login(self, username, password):
        client = self.app.test_client()

        headers = {
            "Content-Type": "application/json"
        }

        data = json.dumps({"username": username, "password": password})

        response = client.post("/auth", data=data, headers=headers)

        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.data)

        self.assertIn("access_token", response_data)

        return response_data["access_token"]

    def test_access_protected_endpoint(self):
        token = self.login("user1", "user1password")

        client = self.app.test_client()

        headers = {
            "Authorization": "JWT {}".format(token)
        }

        response = client.get("/api/v1/stories", headers=headers)

        self.assertEqual(response.status_code, 200)

    def test_fail_to_access_protected_endpoint_with_invalidated_token(self):
        token = self.login("user1", "user1password")

        with self.app.app_context():
            user = User.get_by_username(session, "user1")
            user.reset_token_identifier()
            try:
                session.commit()
            except Exception:
                self.fail("Failed to reset the user jti")

        client = self.app.test_client()

        headers = {
            "Authorization": "JWT {}".format(token)
        }

        response = client.get("/api/v1/stories", headers=headers)

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
