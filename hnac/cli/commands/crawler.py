from flask_script import Command
from flask import current_app

from hnac.crawlers import create_hackernews_api_crawler_job


class Crawl(Command):
    """Start the crawler"""

    def run(self):
        job = create_hackernews_api_crawler_job(current_app.config)

        job.run()
