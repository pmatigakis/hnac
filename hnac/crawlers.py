import logging
from logging.handlers import RotatingFileHandler

from hnac.jobs import HackernewsStoryDownloader
from hnac.configuration import (HNAC_CRAWLER_SECTION,
                                HNAC_CRAWLER_LOG_FILE,
                                HNAC_CRAWLER_ENABLE_LOGGING,
                                HNAC_CRAWLER_DEBUG,
                                HNAC_CRAWLER_LOG_FILE_SIZE,
                                HNAC_CRAWLER_LOG_FILE_COUNT,
                                DEFAULT_CRAWLER_LOG_FILENAME)


def create_hackernews_api_crawler_job(config):
    if config.getboolean(HNAC_CRAWLER_SECTION,
                         HNAC_CRAWLER_ENABLE_LOGGING):

        log_level = logging.INFO
        if config.getboolean(HNAC_CRAWLER_SECTION, HNAC_CRAWLER_DEBUG):
            log_level = logging.DEBUG

        log_format = "%(asctime)s %(name)s %(levelname)s %(message)s"

        formatter = logging.Formatter(log_format)

        logger = logging.getLogger()

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(log_level)

        logger.addHandler(console_handler)

        log_file = (config.get(HNAC_CRAWLER_SECTION, HNAC_CRAWLER_LOG_FILE)
                    or DEFAULT_CRAWLER_LOG_FILENAME)

        file_handler = RotatingFileHandler(
            log_file,
            mode="a",
            maxBytes=config.getint(HNAC_CRAWLER_SECTION,
                                   HNAC_CRAWLER_LOG_FILE_SIZE),
            backupCount=config.getint(HNAC_CRAWLER_SECTION,
                                      HNAC_CRAWLER_LOG_FILE_COUNT)
        )

        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)

        logger.addHandler(file_handler)

        logger.setLevel(log_level)

    job = HackernewsStoryDownloader(config)

    return job
