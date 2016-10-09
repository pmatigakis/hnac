from datetime import datetime, timedelta
from os.path import abspath, dirname, join
from unittest import TestCase

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError

from hnac.models import Base, User, Report
from hnac import jobs
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

        job_1 = jobs.Job(None, None, None)
        job_1.processed_item_count = 5
        job_1.failed = True
        job_1.id = "job_1_uuid"
        job_1_start_time = datetime(2016, 5, 6, 12, 0, 0)
        job_1_end_time = job_1_start_time + timedelta(seconds=40)
        report_1 = jobs.Report(job_1, job_1_start_time, job_1_end_time)

        Report.save_report(self.session, report_1)

        job_2 = jobs.Job(None, None, None)
        job_2.processed_item_count = 11
        job_2.failed = False
        job_2.id = "job_2_uuid"
        job_2_start_time = datetime(2016, 5, 6, 15, 0, 0)
        job_2_end_time = job_1_start_time + timedelta(seconds=40)
        report_2 = jobs.Report(job_2, job_2_start_time, job_2_end_time)

        Report.save_report(self.session, report_2)

        try:
            session.commit()

            self.test_user_id = user.id
            self.test_user_jti = user.jti
        except SQLAlchemyError:
            session.rollback()
            self.fail("failed to load mock data")

        session.close()


class CommandTestCase(TestCase):
    def setUp(self):
        settings_path = join(dirname(abspath(__file__)), "settings.py")
        self.app = create_app("testing", settings_path)

        engine = session.get_bind()
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

    def tearDown(self):
        engine = session.get_bind()
        Base.metadata.drop_all(engine)

        session.remove()


class CommandTestCaseWithMockData(CommandTestCase):
    def setUp(self):
        super(CommandTestCaseWithMockData, self).setUp()

        self.test_user_username = "user1"
        self.test_user_password = "password"

        user = User.create(session, self.test_user_username, self.test_user_password)

        try:
            session.commit()

            self.test_user_id = user.id
            self.test_user_jti = user.jti
        except SQLAlchemyError as e:
            print e
            session.rollback()
            self.fail("failed to load mock data")
