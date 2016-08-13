from abc import ABCMeta, abstractmethod
import logging

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

        self._db = None

    def configure(self, config):
        connection_string = config["HNAC_COUCHDB_SERVER"]
        database_name = config["HNAC_COUCHDB_DATABASE"]

        logger.debug("Using CouchDB server at %s", connection_string)
        logger.debug("Using CouchDB database %s", database_name)

        server = couchdb.Server(connection_string)
        self._db = server[database_name]

    def process_item(self, source, item):
        if not is_story_item(item):
            logger.warning("item is not a story object")
            return None

        doc = self._db.get("hackernews/item/%d" % item["id"])

        if doc:
            logger.debug("CochDb document with id %s already exists",
                         "hackernews/item/%d" % item["id"])
            doc.update(item)
            item = doc

        try:
            self._db["hackernews/item/%d" % item["id"]] = item
        except HTTPError:
            logger.exception("Failed to save story with id to CouchDB %d",
                             item["id"])
            return None

        return item
