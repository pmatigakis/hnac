import logging

from flask_script import Command
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError

from hnac.crawlers import create_hackernews_api_crawler_job
from hnac.web.database import db
from hnac.models import Report


logger = logging.getLogger(__name__)


class Crawl(Command):
    """Start the crawler"""

    def _run_hackernews_crawl_job(self):
        job = create_hackernews_api_crawler_job(current_app.config, db.session)
        logger.info("running hackernews crawl job %s", job.id)
        job_execution_result = job.run()

        Report.save_report(db.session, job_execution_result)

        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            logger.exception(
                "failed to save job execution results for job %s", job.id)
            return

        logger.info("executed hackernews crawl job %s", job.id)

    def run(self):
        """Start the crawler"""
        try:
            self._run_hackernews_crawl_job()
        except (KeyboardInterrupt, SystemExit):
            db.session.rollback()
            logger.info("crawler stopped by user or system")
        except Exception:
            db.session.rollback()
            logger.exception("failed to execute hackernews crawl job")
