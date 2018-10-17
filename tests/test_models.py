from datetime import datetime, timedelta
from unittest import main

from sqlalchemy.exc import SQLAlchemyError
from dateutil.tz import tzutc

from hnac.models import User, Report, Story
from hnac.jobs import Job, JobExecutionResult
from hnac.web.database import db
from hnac.web.queries.operations import EQ, LTE, GTE

from common import ModelTestCase, ModelTestCaseWithMockData
from mock_data import load_stories_1


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


class StorySearchTests(ModelTestCase):
    def setUp(self):
        super(StorySearchTests, self).setUp()

        with self.app.app_context():
            load_stories_1(db.session)

            try:
                db.session.commit()
            except SQLAlchemyError:
                db.session.rollback()
                self.fail("failed to load mock stories")

    def test_search(self):
        criteria = [
            ("username", EQ, "user_1"),
            ("score", LTE, 20),
            ("score", GTE, 5)
        ]

        with self.app.app_context():
            stories = Story.search(
                session=db.session,
                criteria=criteria,
                offset=0,
                limit=500,
                order_by=Story.score,
                sort_desc=False
            )

            self.assertEqual(len(stories), 3)
            self.assertEqual(stories[0].id, 4)
            self.assertEqual(stories[1].id, 2)
            self.assertEqual(stories[2].id, 1)

    def test_search_with_defaults(self):
        criteria = [
            ("username", EQ, "user_1"),
            ("score", LTE, 20),
            ("score", GTE, 5)
        ]

        with self.app.app_context():
            stories = Story.search(
                session=db.session,
                criteria=criteria
            )

            self.assertEqual(len(stories), 3)
            self.assertEqual(stories[0].id, 1)
            self.assertEqual(stories[1].id, 2)
            self.assertEqual(stories[2].id, 4)

    def test_search_with_desc_sorting(self):
        criteria = [
            ("username", EQ, "user_1"),
            ("score", LTE, 20),
            ("score", GTE, 5)
        ]

        with self.app.app_context():
            stories = Story.search(
                session=db.session,
                criteria=criteria,
                offset=0,
                limit=500,
                order_by=Story.score,
                sort_desc=True
            )

            self.assertEqual(len(stories), 3)
            self.assertEqual(stories[2].id, 4)
            self.assertEqual(stories[1].id, 2)
            self.assertEqual(stories[0].id, 1)

    def test_search_with_limit_and_offset(self):
        criteria = [
            ("username", EQ, "user_1"),
            ("score", LTE, 20),
            ("score", GTE, 5)
        ]

        with self.app.app_context():
            stories = Story.search(
                session=db.session,
                criteria=criteria,
                offset=1,
                limit=2,
                order_by=Story.score,
                sort_desc=True
            )

            self.assertEqual(len(stories), 2)
            self.assertEqual(stories[1].id, 4)
            self.assertEqual(stories[0].id, 2)


class StoryRetrievalTests(ModelTestCase):
    def setUp(self):
        super(StoryRetrievalTests, self).setUp()

        with self.app.app_context():
            load_stories_1(db.session)

            try:
                db.session.commit()
            except SQLAlchemyError:
                db.session.rollback()
                self.fail("failed to load mock stories")

    def test_yield_in_period(self):
        from_date = datetime(2018, 6, 21, 20, 46, 0, tzinfo=tzutc())
        to_date = datetime(2018, 6, 21, 20, 46, 30, tzinfo=tzutc())

        with self.app.app_context():
            story_ids = [
                story.story_id
                for story in Story.yield_in_period(
                    db.session, from_date, to_date)
            ]

            self.assertEqual(
                story_ids,
                [4, 2, 1]
            )


if __name__ == '__main__':
    main()
