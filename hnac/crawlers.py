import logging
from logging.handlers import RotatingFileHandler

from hnac.jobs import Job


def create_hackernews_api_crawler_job(config):
    if config["HNAC_CRAWLER_ENABLE_LOGGING"]:

        log_level = config["HNAC_CRAWLER_LOG_LEVEL"]

        log_format = config["HNAC_CRAWLER_LOG_FORMAT"]

        formatter = logging.Formatter(log_format)

        logger = logging.getLogger()

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(log_level)

        logger.addHandler(console_handler)

        log_file = config["HNAC_CRAWLER_LOG_FILE"]

        file_handler = RotatingFileHandler(
            log_file,
            mode="a",
            maxBytes=config["HNAC_CRAWLER_LOG_FILE_SIZE"],
            backupCount=config["HNAC_CRAWLER_LOG_FILE_COUNT"]
        )

        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)

        logger.addHandler(file_handler)

        logger.setLevel(log_level)

    source = config["SOURCE"]()
    source.configure(config)

    processors = [processor() for processor in config["PROCESSORS"]]

    for processor in processors:
        processor.configure(config)

    job = Job(config, source, processors)

    return job
