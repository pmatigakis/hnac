from datetime import datetime, timedelta
from unittest import main

from sqlalchemy.exc import SQLAlchemyError

from hnac.models import User, Report as Report
from hnac.jobs import Job, JobExecutionResult
from hnac.web.database import db

from common import ModelTestCase, ModelTestCaseWithMockData


class UserCreationTests(ModelTestCase):
    def test_create_api_user(self):
        with self.app.app_context():
            user = User.create(db.session, "user1", "password")

            self.assertIsNotNone(user)

            try:
                db.session.commit()
            except SQLAlchemyError:
                db.session.rollback()
                self.fail("failed to create user")

            self.assertIsNotNone(user.id)
            self.assertEqual(user.username, "user1")
            self.assertIsNotNone(user.password)
            self.assertTrue(user.active)
            self.assertIsNotNone(user.registered_at)
            self.assertIsNotNone(user.jti)


class UserQueryTests(ModelTestCaseWithMockData):
    def test_get_user_by_username(self):
        with self.app.app_context():
            user = User.get_by_username(db.session, self.test_user_username)

            self.assertIsNotNone(user)
            self.assertIsNotNone(user.id)
            self.assertEqual(user.username, self.test_user_username)
            self.assertIsNotNone(user.password)
            self.assertTrue(user.active)
            self.assertIsNotNone(user.registered_at)


class userRemovalTests(ModelTestCaseWithMockData):
    def test_delete_user(self):
        with self.app.app_context():
            user = User.delete(db.session, self.test_user_username)

            self.assertIsNotNone(user)

            try:
                db.session.commit()
            except SQLAlchemyError:
                db.session.rollback()
                self.fail("failed to delete user")

            user = db.session.query(User)\
                             .filter_by(username=self.test_user_username)\
                             .one_or_none()

            self.assertIsNone(user)


class UserPasswordManagementTests(ModelTestCaseWithMockData):
    def test_change_user_password(self):
        with self.app.app_context():
            user = User.get_by_username(db.session, self.test_user_username)

            original_jti = user.jti
            original_password = user.password

            new_password = "new_{}".format(self.test_user_password)

            user.change_password(new_password)

            try:
                db.session.commit()
            except SQLAlchemyError:
                db.session.rollback()
                self.fail("failed to change user password")

            self.assertIsNotNone(user.password)

            self.assertNotEqual(user.password, original_password)
            self.assertNotEqual(user.jti, original_jti)


class UserAuthenticationTests(ModelTestCaseWithMockData):
    def test_authenticate_user(self):
        with self.app.app_context():
            user = User.authenticate(db.session, self.test_user_username,
                                     self.test_user_password)

            self.assertIsNotNone(user)

    def test_fail_to_authenticate_with_invalid_password(self):
        password = "invalid_{}".format(self.test_user_password)

        with self.app.app_context():
            user = User.authenticate(db.session,
                                     self.test_user_username, password)

            self.assertIsNone(user)

    def test_fail_to_authenticate_unknown_user(self):
        with self.app.app_context():
            user = User.authenticate(db.session, "unknown-user",
                                     self.test_user_password)

            self.assertIsNone(user)

    def test_reset_user_token_jti(self):
        with self.app.app_context():
            user = User.get_by_username(db.session, self.test_user_username)

            original_jti = user.jti

            user.reset_token_identifier()

            self.assertNotEqual(user.jti, original_jti)

    def test_authenticate_using_jwt(self):
        with self.app.app_context():
            user = User.authenticate_using_jwt(db.session, self.test_user_id,
                                               self.test_user_jti)

            self.assertIsNotNone(user)
            self.assertEqual(user.jti, self.test_user_jti)
            self.assertEqual(user.id, self.test_user_id)

    def test_fail_to_authenticate_using_jwt_with_invalid_user_id(self):
        with self.app.app_context():
            user = User.authenticate_using_jwt(db.session, 1234,
                                               self.test_user_jti)

            self.assertIsNone(user)

    def test_fail_to_authenticate_using_jwt_with_invalid_jti(self):
        with self.app.app_context():
            user = User.authenticate_using_jwt(
                db.session, self.test_user_id, "invalid-jti")

            self.assertIsNone(user)


class JobResultTests(ModelTestCase):
    def test_save_job_result(self):
        job = Job(None, None)

        start_time = datetime(2016, 4, 5, 12, 0, 0)
        end_time = start_time + timedelta(seconds=50)
        report = JobExecutionResult(
            job=job,
            start_time=start_time,
            end_time=end_time,
            failed=True,
            processed_item_count=12
        )

        with self.app.app_context():
            report_object = Report.save_report(db.session, report)

            self.assertIsNotNone(report_object)
            self.assertIsNone(report_object.id)

            try:
                db.session.commit()
            except SQLAlchemyError:
                db.session.rollback()
                self.fail("failed to save job results")

            self.assertIsNotNone(report_object.id)
            self.assertEqual(report_object.job_id, job.id)
            self.assertEqual(report_object.started_at, start_time)
            self.assertEqual(report_object.completed_at, end_time)
            self.assertEqual(report_object.num_processed_items, 12)
            self.assertTrue(report_object.failed)


class JobRetrievalTests(ModelTestCaseWithMockData):
    def test_get_latest(self):
        with self.app.app_context():
            latest_reports = Report.get_latest(db.session)

            self.assertEqual(len(latest_reports), 2)

            self.assertEqual(latest_reports[0].job_id, "job_2_uuid")
            self.assertEqual(latest_reports[1].job_id, "job_1_uuid")


if __name__ == '__main__':
    main()
