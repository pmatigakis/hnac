from abc import ABCMeta, abstractmethod
import logging
from time import time

import couchdb
from couchdb.http import HTTPError

from hnac.schemas import is_story_item


logger = logging.getLogger(__name__)


class Processor(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def process_item(self, source, item):
        pass

    def configure(self, config):
        pass

    def job_started(self, job):
        pass

    def job_finished(self, job):
        pass


class CouchDBStorage(Processor):
    def __init__(self):
        super(CouchDBStorage, self).__init__()

        self.update_delta = 3600

        self._db = None

    def _init_database(self, host, database_name):
        server = couchdb.Server(host)
        self._db = server[database_name]

    def configure(self, config):
        connection_string = config["COUCHDB_SERVER"]
        database_name = config["COUCHDB_DATABASE"]

        logger.info("Using CouchDB server at %s", connection_string)
        logger.info("Using CouchDB database %s", database_name)

        self._init_database(connection_string, database_name)

        self.update_delta = config["CRAWLER_STORY_UPDATE_DELTA"]

    def process_item(self, source, item):
        if not is_story_item(item):
            logger.warning("item is not a story object")
            return item

        story_id = item["id"]
        doc_id = "hackernews/item/%d" % story_id

        doc = self._db.get(doc_id)

        if doc:
            logger.debug("CouchDb document with id %s already exists", doc_id)

            if doc["updated_at"] + self.update_delta > time():
                logger.debug("Story with id %d doesn't need update", story_id)
                return item
        else:
            doc = {}

        doc["updated_at"] = time()
        doc["data"] = item

        try:
            self._db[doc_id] = doc
        except HTTPError:
            logger.exception("Failed to save story with id to CouchDB %d",
                             story_id)
            return None

        return item
