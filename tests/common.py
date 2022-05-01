import importlib
from datetime import datetime, timedelta
from os.path import abspath, dirname, join
from unittest import TestCase
import json
from os import environ

from sqlalchemy.exc import SQLAlchemyError

from hnac.models import User, Report, Token
from hnac.jobs import JobExecutionResult, Job
from hnac.web.app import create_app
from hnac.web.database import db


class ModelTestCase(TestCase):
    def setUp(self):
        settings_path = join(dirname(abspath(__file__)), "test_env")
        environ["CONFIGURATION_FILE"] = settings_path
        import hnac.configuration.settings
        importlib.reload(hnac.configuration.settings)
        self.app = create_app()

        with self.app.app_context():
            db.create_all()


class ModelTestCaseWithMockData(ModelTestCase):
    def setUp(self):
        super(ModelTestCaseWithMockData, self).setUp()

        self.test_user_username = "user1"
        self.test_user_password = "password"
        self.test_token_name = "token_1"

        with self.app.app_context():
            token = Token.create(db.session, self.test_token_name)

            user = User.create(db.session, self.test_user_username,
                               self.test_user_password)
            user.id = 1

            job_1 = Job(None, None)
            job_1.id = "job_1_uuid"
            job_1_start_time = datetime(2016, 5, 6, 12, 0, 0)
            job_1_end_time = job_1_start_time + timedelta(seconds=40)
            report_1 = JobExecutionResult(
                job=job_1,
                start_time=job_1_start_time,
                end_time=job_1_end_time,
                failed=True,
                processed_item_count=5
            )

            Report.save_report(db.session, report_1)

            job_2 = Job(None, None)
            job_2.id = "job_2_uuid"
            job_2_start_time = datetime(2016, 5, 6, 15, 0, 0)
            job_2_end_time = job_1_start_time + timedelta(seconds=40)
            report_2 = JobExecutionResult(
                job=job_2,
                start_time=job_2_start_time,
                end_time=job_2_end_time,
                failed=False,
                processed_item_count=11
            )

            Report.save_report(db.session, report_2)

            try:
                db.session.commit()
            except SQLAlchemyError:
                db.session.rollback()
                self.fail("failed to load mock data")
            self.test_user_id = user.id
            self.test_token_id = token.id
            self.test_token = token.value


class WebTestCase(TestCase):
    def setUp(self):
        settings_path = join(dirname(abspath(__file__)), "test_env")
        environ["CONFIGURATION_FILE"] = settings_path
        import hnac.configuration.settings
        importlib.reload(hnac.configuration.settings)
        self.app = create_app()

        with self.app.app_context():
            db.create_all()

        self.client = self.app.test_client()

    def authenticate_using_jwt(self, username, password):
        headers = {
            "Content-Type": "application/json"
        }

        data = json.dumps({"username": username, "password": password})

        response = self.client.post("/auth", data=data, headers=headers)

        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.data.decode("utf8"))

        self.assertIn("access_token", response_data)

        return response_data["access_token"]


class WebTestCaseWithUserAccount(WebTestCase):
    def setUp(self):
        super(WebTestCaseWithUserAccount, self).setUp()

        self.client = self.app.test_client()

        self.test_user_username = "user1"
        self.test_user_password = "password"
        self.test_token_name = "token_1"

        with self.app.app_context():
            token = Token.create(db.session, self.test_token_name)

            user1 = User.create(db.session, self.test_user_username,
                                self.test_user_password)

            try:
                db.session.commit()
            except SQLAlchemyError:
                db.session.rollback()
                self.fail("failed to load mock data")

            self.test_user_id = user1.id
            self.test_token_id = token.id
            self.test_token = token.value


class CommandTestCase(WebTestCase):
    pass


class CommandTestCaseWithMockData(WebTestCaseWithUserAccount):
    pass
