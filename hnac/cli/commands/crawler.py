from flask_script import Command
from flask import current_app

from hnac.crawlers import create_hackernews_api_crawler_job
from hnac.web import session
from hnac.models import Report


class Crawl(Command):
    """Start the crawler"""

    def run(self):
        job = create_hackernews_api_crawler_job(current_app.config)

        report = job.run()

        Report.save_report(session, report)

        session.commit()
