from abc import ABCMeta, abstractmethod
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from hnac.queries.stories import save_or_update_story
from hnac.models import Base
from hnac.configuration import HNAC_DB_SECTION, HNAC_DB


logger = logging.getLogger(__name__)


def is_story_item(item_data):
    required_fields = set(["id", "type", "by", "descendants",
                           "score", "time", "title", "url"])

    fields = set(item_data.keys())

    if not required_fields.issubset(fields):
        return False

    if item_data["type"] != "story":
        return False

    return True


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

    def configure(self, config):
        self._db = config.get(HNAC_DB_SECTION, HNAC_DB)

        logger.debug("db connection string %s", self._db)

    def job_started(self, job):
        engine = create_engine(self._db)

        Base.metadata.create_all(engine)

        self._session = scoped_session(sessionmaker(bind=engine))

    def job_finished(self, job):
        self._session.remove()

    def process_item(self, source, item):
        if not is_story_item(item):
            logger.debug("item is not a story object")
            return

        try:
            save_or_update_story(self._session, item)
        except:
            logger.error("failed to save or update story %d", item["id"])
