import logging

from hnac.jobs import HackernewsCrawlJob
from hnac.processors import SQLAlchemyStorage
from hnac.utilities.modules import import_string


logger = logging.getLogger(__name__)


def create_hackernews_api_crawler_job(config, session):
    """Create the job that will crawl hackernews

    :param dict config: the job configuration
    :param Session session: the sqlalchemy Session object to use
    :rtype: HackernewsCrawlJob
    :return: the job object
    """
    logger.info("Initializing data processors")
    processors = [SQLAlchemyStorage(session)]
    processors.extend([
        import_string(processor)() for processor in config["PROCESSORS"]
    ])

    for processor in processors:
        processor.configure(config)
    logger.info("Data processors initialized")

    job = HackernewsCrawlJob(config, processors)
    logger.info("Created job with id %s", job.id)

    return job
