from datetime import datetime, timedelta
from unittest import TestCase, main
from os.path import abspath, dirname, join

from sqlalchemy import create_engine
from mock import patch

from hnac.web.app import create_app
from hnac.cli.commands.crawler import Crawl
from hnac.models import Base, Report as ReportModel
from hnac.web import session
from hnac.jobs import Report


class CrawlTests(TestCase):
    def setUp(self):
        settings_path = join(dirname(abspath(__file__)), "settings.py")
        self.app = create_app("testing", settings_path)

        engine = create_engine("sqlite:///test.db")
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

    def tearDown(self):
        session.remove()

    @patch("hnac.cli.commands.crawler.create_hackernews_api_crawler_job")
    def test_run(self, mock):
        class MockJob(object):
            def __init__(self):
                self.id = "this_is_an_uuid"
                self.processed_item_count = 13
                self.failed = True

            def run(self):
                start_time = datetime(2016, 4, 6, 12, 00, 00)
                end_time = start_time + timedelta(seconds=30)

                return Report(self, start_time, end_time)

        mock.return_value = MockJob()

        crawl = Crawl()

        with self.app.app_context():
            crawl.run()

            report = session.query(ReportModel).one()

            self.assertIsNotNone(report)

            self.assertEqual(report.job_id, "this_is_an_uuid")
            self.assertEqual(report.num_processed_items, 13)
            self.assertTrue(report.failed)

            started_at = datetime(2016, 4, 6, 12, 00, 00)
            self.assertEqual(report.started_at, started_at)

            completed_at = started_at + timedelta(seconds=30)
            self.assertEqual(report.completed_at, completed_at)


if __name__ == "__main__":
    main()
