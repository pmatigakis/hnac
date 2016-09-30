from datetime import datetime, timedelta
from unittest import TestCase, main

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from hnac.models import Base, User, Report as Report
from hnac import jobs


class UserCreationTests(TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")

        Base.metadata.create_all(self.engine)

        self.Session = scoped_session(sessionmaker(bind=self.engine))

    def tearDown(self):
        self.Session.remove()

    def test_create_api_user(self):
        session = self.Session()

        user = User.create(session, "user1", "password")

        self.assertIsNotNone(user)

        session.commit()

        self.assertIsNotNone(user.id)
        self.assertEqual(user.username, "user1")
        self.assertIsNotNone(user.password)
        self.assertTrue(user.active)
        self.assertIsNotNone(user.registered_at)
        self.assertIsNotNone(user.jti)

        session.close()


class UserQueryTests(TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")

        Base.metadata.create_all(self.engine)

        self.Session = scoped_session(sessionmaker(bind=self.engine))

        session = self.Session()

        self.username = "user1"
        self.user = User.create(session, self.username, "password")
        session.commit()

        session.close()

    def tearDown(self):
        self.Session.remove()

    def test_get_user_by_username(self):
        session = self.Session()

        user = User.get_by_username(session, self.username)

        self.assertIsNotNone(user)
        self.assertIsNotNone(user.id)
        self.assertEqual(user.username, self.username)
        self.assertIsNotNone(user.password)
        self.assertTrue(user.active)
        self.assertIsNotNone(user.registered_at)

        session.close()

    def test_delete_user(self):
        session = self.Session()

        user = User.delete(session, self.username)

        self.assertIsNotNone(user)

        session.commit()

        user = session.query(User)\
                      .filter_by(username=self.username)\
                      .one_or_none()

        self.assertIsNone(user)


class UserPasswordManagementTests(TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")

        Base.metadata.create_all(self.engine)

        self.Session = scoped_session(sessionmaker(bind=self.engine))

        session = self.Session()

        self.username = "user1"
        self.password = "password"
        self.user = User.create(session, self.username, self.password)
        session.commit()

        session.close()

    def tearDown(self):
        self.Session.remove()

    def test_change_user_password(self):
        session = self.Session()

        user = User.get_by_username(session, self.username)

        original_jti = user.jti
        original_password = user.password

        new_password = "new_{}".format(self.password)

        user.change_password(new_password)
        session.commit()

        self.assertIsNotNone(user.password)

        self.assertNotEqual(user.password, original_password)
        self.assertNotEqual(user.jti, original_jti)

        session.close()


class UserAuthenticationTests(TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")

        Base.metadata.create_all(self.engine)

        self.Session = scoped_session(sessionmaker(bind=self.engine))

        session = self.Session()

        self.unknown_user = "unknown_user"
        self.username = "user1"
        self.password = "password"
        user = User.create(session, self.username, self.password)
        session.commit()

        self.user_id = user.id
        self.jti = user.jti

        session.close()

    def tearDown(self):
        self.Session.remove()

    def test_authenticate_user(self):
        session = self.Session()

        user = User.authenticate(session, self.username, self.password)

        self.assertIsNotNone(user)

    def test_fail_to_authenticate_with_invalid_password(self):
        session = self.Session()

        password = "invalid_{}".format(self.password)

        user = User.authenticate(session, self.username, password)

        self.assertIsNone(user)

    def test_fail_to_authenticate_unknown_user(self):
        session = self.Session()

        user = User.authenticate(session, self.unknown_user, self.password)

        self.assertIsNone(user)

    def test_reset_user_token_jti(self):
        session = self.Session()
        user = User.get_by_username(session, self.username)

        original_jti = user.jti

        user.reset_token_identifier()

        self.assertNotEqual(user.jti, original_jti)

    def test_authenticate_using_jwt(self):
        session = self.Session()

        user = User.authenticate_using_jwt(session, self.user_id, self.jti)

        self.assertIsNotNone(user)
        self.assertEqual(user.jti, self.jti)
        self.assertEqual(user.id, self.user_id)

    def test_fail_to_authenticate_using_jwt_with_invalid_user_id(self):
        session = self.Session()

        user = User.authenticate_using_jwt(session, 1234, self.jti)

        self.assertIsNone(user)

    def test_fail_to_authenticate_using_jwt_with_invalid_jti(self):
        session = self.Session()

        user = User.authenticate_using_jwt(
            session, self.user_id, "invalid-jti")

        self.assertIsNone(user)


class JobResultTests(TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")

        Base.metadata.create_all(self.engine)

        self.Session = scoped_session(sessionmaker(bind=self.engine))

        session = self.Session()

        self.unknown_user = "unknown_user"
        self.username = "user1"
        self.password = "password"
        self.user = User.create(session, self.username, self.password)
        session.commit()

        session.close()

    def tearDown(self):
        self.Session.remove()

    def test_save_job_result(self):
        session = self.Session()

        job = jobs.Job(None, None, None)
        job.processed_item_count = 12
        job.failed = True

        start_time = datetime(2016, 04, 05, 12, 0, 0)
        end_time = start_time + timedelta(seconds=50)
        report = jobs.Report(job, start_time, end_time)

        report_object = Report.save_report(session, report)

        self.assertIsNotNone(report_object)
        self.assertIsNone(report_object.id)

        session.commit()

        self.assertIsNotNone(report_object.id)
        self.assertEqual(report_object.job_id, job.id)
        self.assertEqual(report_object.started_at, start_time)
        self.assertEqual(report_object.completed_at, end_time)
        self.assertEqual(report_object.num_processed_items, 12)
        self.assertTrue(report_object.failed)

    def test_get_latest(self):
        session = self.Session()

        job_1 = jobs.Job(None, None, None)
        job_1.processed_item_count = 5
        job_1.failed = True
        job_1.id = "job_1_uuid"
        job_1_start_time = datetime(2016, 5, 6, 12, 0, 0)
        job_1_end_time = job_1_start_time + timedelta(seconds=40)
        report_1 = jobs.Report(job_1, job_1_start_time, job_1_end_time)

        Report.save_report(session, report_1)

        job_2 = jobs.Job(None, None, None)
        job_2.processed_item_count = 11
        job_2.failed = False
        job_2.id = "job_2_uuid"
        job_2_start_time = datetime(2016, 5, 6, 15, 0, 0)
        job_2_end_time = job_1_start_time + timedelta(seconds=40)
        report_2 = jobs.Report(job_2, job_2_start_time, job_2_end_time)

        Report.save_report(session, report_2)

        session.commit()

        latest_reports = Report.get_latest(session)

        self.assertEqual(len(latest_reports), 2)

        self.assertEqual(latest_reports[0].job_id, "job_2_uuid")
        self.assertEqual(latest_reports[1].job_id, "job_1_uuid")


if __name__ == '__main__':
    main()
