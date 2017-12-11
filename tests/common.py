from datetime import datetime, timedelta
from os.path import abspath, dirname, join
from unittest import TestCase
import json

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError

from hnac.models import Base, User, Report
from hnac.jobs import JobExecutionResult, Job
from hnac.web.app import create_app
from hnac.web import session


class ModelTestCase(TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")

        Base.metadata.create_all(self.engine)

        self.Session = scoped_session(sessionmaker(bind=self.engine))

        self.session = self.Session()

    def tearDown(self):
        self.session.close()

        self.Session.remove()


class ModelTestCaseWithMockData(ModelTestCase):
    def setUp(self):
        super(ModelTestCaseWithMockData, self).setUp()

        session = self.Session()

        self.test_user_username = "user1"
        self.test_user_password = "password"

        user = User.create(session, self.test_user_username,
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

        Report.save_report(self.session, report_1)

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

        Report.save_report(self.session, report_2)

        try:
            session.commit()

            self.test_user_id = user.id
            self.test_user_jti = user.jti
        except SQLAlchemyError:
            session.rollback()
            self.fail("failed to load mock data")

        session.close()


class WebTestCase(TestCase):
    def setUp(self):
        settings_path = join(dirname(abspath(__file__)), "settings.py")
        self.app = create_app("testing", settings_path)

        engine = session.get_bind()
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

        self.client = self.app.test_client()

    def tearDown(self):
        engine = session.get_bind()
        Base.metadata.drop_all(engine)

        session.remove()

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

        self.test_user_username = "user1"
        self.test_user_password = "password"

        user1 = User.create(session, self.test_user_username,
                            self.test_user_password)

        try:
            session.commit()

            self.test_user_id = user1.id
            self.test_user_jti = user1.jti
        except SQLAlchemyError as e:
            session.rollback()
            self.fail("failed to load mock data")


class CommandTestCase(WebTestCase):
    pass


class CommandTestCaseWithMockData(WebTestCaseWithUserAccount):
    pass
