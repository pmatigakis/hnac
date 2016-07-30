from abc import ABCMeta, abstractmethod
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError

from hnac.models import Base, Story


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
        self._db = config["HNAC_DB"]

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

        if item.data["type"] != "story":
            logger.debug("item is not a story object")
            return None

        story_id = item.data["id"]

        story = Story.get_by_id(self._session, story_id)

        if not story:
            story = Story.create_from_dict(self._session, item.data)
        else:
            story = Story.update_from_dict(self._session, item.data)

        try:
            self._session.commit()
        except SQLAlchemyError:
            logger.error("failed to save or update story %d", story_id)

            self._session.rollback()

            return None

        return story
