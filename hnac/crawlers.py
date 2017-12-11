import logging

from hnac.jobs import Job
from hnac.sources import HackernewsStories
from hnac.processors import CouchDBStorage, SQLAlchemyStorage
from hnac.utilities.modules import import_string


logger = logging.getLogger(__name__)


def create_hackernews_api_crawler_job(config, session):
    logger.info("Initializing data source")
    source = HackernewsStories()
    source.configure(config)

    logger.info("Initializing data processors")

    # processors = [CouchDBStorage()]
    processors = [SQLAlchemyStorage(session)]
    processors.extend([
        import_string(processor)() for processor in config["PROCESSORS"]
    ])

    for processor in processors:
        processor.configure(config)

    logger.info("Data processors initialized")

    job = Job(config, source, processors)

    logger.info("Created job with id %s", job.id)

    return job
