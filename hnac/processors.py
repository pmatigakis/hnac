from abc import ABCMeta, abstractmethod
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError
import couchdb
from couchdb.http import HTTPError

from hnac.models import Base, Story
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


class SQLAlchemyStorage(Processor):
    def __init__(self):
        super(SQLAlchemyStorage, self).__init__()

        self._session = None
        self._db = None

    def configure(self, config):
        self._db = config["HNAC_SQLALCHEMY_DATABASE"]

        logger.debug("db connection string %s", self._db)

    def job_started(self, job):
        engine = create_engine(self._db)

        Base.metadata.create_all(engine)

        self._session = scoped_session(sessionmaker(bind=engine))

    def job_finished(self, job):
        self._session.remove()

    def process_item(self, source, item):
        if not item:
            return None

        if item["type"] != "story":
            logger.warning("item is not a story object")
            return None

        story_id = item["id"]

        story = Story.get_by_id(self._session, story_id)

        if not story:
            logger.debug("Saving story with id %d", story_id)
            story = Story.create_from_dict(self._session, item)
        else:
            logger.debug("Updating story with id %d", story_id)
            story = Story.update_from_dict(self._session, item)

        try:
            self._session.commit()
        except SQLAlchemyError:
            self._session.rollback()
            
            logger.exception("failed to save or update story %d", story_id)

            return None

        return story

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
