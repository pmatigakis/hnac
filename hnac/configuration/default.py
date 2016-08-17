import logging

from hnac.sources import HackernewsStories


SECRET_KEY = "secret"
TESTING = False
DEBUG = False

HNAC_CRAWLER_LOG_FILE = "hnac_crawler.log"
HNAC_CRAWLER_ENABLE_LOGGING = False
HNAC_CRAWLER_LOG_LEVEL = logging.INFO
HNAC_CRAWLER_LOG_FILE_SIZE = 2 ** 24
HNAC_CRAWLER_LOG_FILE_COUNT = 5
HNAC_CRAWLER_LOG_FORMAT = "%(asctime)s %(name)s %(levelname)s %(message)s"
HNAC_CRAWLER_WAIT_TIME = 1.0
HNAC_CRAWLER_BACKOFF_TIME = 1.0
HNAC_CRAWLER_ABORT_AFTER = 3
HNAC_CRAWLER_STORY_UPDATE_DELTA = 3600

HNAC_DB = "sqlite:///:memory:"

HNAC_SQLALCHEMY_DATABASE = "sqlite:///:memory:"

HNAC_COUCHDB_SERVER = "http://localhost:5984"
HNAC_COUCHDB_DATABASE = "hnac"


HNAC_API_HOST = "127.0.0.1"
HNAC_API_PORT = 5000

HNAC_API_ENABLE_LOGGING = False
HNAC_API_LOG_FILE = "hnac_api.log"
HNAC_API_LOG_LEVEL = logging.INFO
HNAC_API_LOG_FILE_SIZE = 2 ** 24
HNAC_API_LOG_FILE_COUNT = 5
HNAC_API_LOG_FORMAT = "%(asctime)s %(name)s %(levelname)s %(message)s"

HNAC_API_ENVIRONMENT = "production"

SOURCE = HackernewsStories

PROCESSORS = [
]

HNAC_COUCHDB_SERVER = "http://localhost:5984"
HNAC_COUCHDB_DATABASE = "hnac"