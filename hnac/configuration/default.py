import logging

from hnac.sources import HackernewsStories
from hnac.processors import CouchDBStorage


SECRET_KEY = "secret"
TESTING = False
DEBUG = False

CRAWLER_LOG_FILE = "hnac_crawler.log"
CRAWLER_ENABLE_LOGGING = False
CRAWLER_LOG_LEVEL = logging.INFO
CRAWLER_LOG_FILE_SIZE = 2 ** 24
CRAWLER_LOG_FILE_COUNT = 5
CRAWLER_LOG_FORMAT = "%(asctime)s %(name)s %(levelname)s %(message)s"
CRAWLER_WAIT_TIME = 1.0
CRAWLER_BACKOFF_TIME = 1.0
CRAWLER_ABORT_AFTER = 3
CRAWLER_STORY_UPDATE_DELTA = 3600

API_HOST = "127.0.0.1"
API_PORT = 5000

API_ENABLE_LOGGING = False
API_LOG_FILE = "hnac_api.log"
API_LOG_LEVEL = logging.INFO
API_LOG_FILE_SIZE = 2 ** 24
API_LOG_FILE_COUNT = 5
API_LOG_FORMAT = "%(asctime)s %(name)s %(levelname)s %(message)s"

API_ENVIRONMENT = "production"

SOURCE = HackernewsStories

PROCESSORS = [
    CouchDBStorage
]

PROPAGATE_EXCEPTIONS = True
