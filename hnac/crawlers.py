import logging
from logging.handlers import RotatingFileHandler

from hnac.jobs import Job


logger = logging.getLogger(__name__)


def create_hackernews_api_crawler_job(config):
    if config["CRAWLER_ENABLE_LOGGING"]:

        log_level = config["CRAWLER_LOG_LEVEL"]

        log_format = config["CRAWLER_LOG_FORMAT"]

        formatter = logging.Formatter(log_format)

        logger = logging.getLogger()

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(log_level)

        logger.addHandler(console_handler)

        log_file = config["CRAWLER_LOG_FILE"]

        file_handler = RotatingFileHandler(
            log_file,
            mode="a",
            maxBytes=config["CRAWLER_LOG_FILE_SIZE"],
            backupCount=config["CRAWLER_LOG_FILE_COUNT"]
        )

        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)

        logger.addHandler(file_handler)

        logger.setLevel(log_level)

    logger.debug("Initializing data source")
    source = config["SOURCE"]()
    source.configure(config)

    logger.debug("Initializing data processors")
    processors = [processor() for processor in config["PROCESSORS"]]

    for processor in processors:
        processor.configure(config)

    job = Job(config, source, processors)

    logger.info("created job with id %s", job.id)

    return job
