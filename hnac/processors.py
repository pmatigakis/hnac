from abc import ABCMeta, abstractmethod
import logging
from time import time
from datetime import datetime

import couchdb
from couchdb.http import HTTPError
from sqlalchemy.exc import SQLAlchemyError

from hnac.schemas import is_story_item
from hnac.models import HackernewsUser, Url, Story
from hnac.queues import create_publisher_from_config


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

    def _init_database(self, host, database_name):
        server = couchdb.Server(host)
        self._db = server[database_name]

    def configure(self, config):
        connection_string = config["COUCHDB_SERVER"]
        database_name = config["COUCHDB_DATABASE"]

        logger.info("Using CouchDB server at %s", connection_string)
        logger.info("Using CouchDB database %s", database_name)

        self._init_database(connection_string, database_name)

    def process_item(self, source, item):
        if not is_story_item(item):
            logger.warning("item is not a story object")
            return True

        story_id = item["id"]
        doc_id = "hackernews/item/%d" % story_id

        doc = self._db.get(doc_id)

        current_time = time()
        if doc is None:
            # the document doesn't exist so we have to create it
            doc = {
                "created_at": current_time
            }

        doc["updated_at"] = current_time
        doc["data"] = item

        logger.info("saving story with id %s to couchdb", story_id)

        try:
            self._db[doc_id] = doc
        except HTTPError:
            logger.exception("Failed to save story with id to CouchDB %d",
                             story_id)
            return False

        return True


class DummyProcessor(Processor):
    def process_item(self, source, item):
        print(item)

        return True


class SQLAlchemyStorage(Processor):
    def __init__(self, session):
        self._session = session

    def _create_story(self, story_data):
        story_id = story_data["id"]

        logger.info("creating story object with story id %s", story_id)

        username = story_data["by"]
        user = HackernewsUser.get_or_create_by_username(
            session=self._session,
            username=username
        )

        url = story_data["url"]
        url_object = Url.get_or_create_by_url(self._session, url)

        story = Story.create(
            session=self._session,
            url=url_object,
            user=user,
            story_id=story_id,
            title=story_data["title"],
            score=story_data["score"],
            time=story_data["time"],
            descendants=story_data["descendants"]
        )

        return story

    def _update_story(self, story, story_data):
        logger.info("updating story object with story id %s", story.story_id)

        story.score = story_data["score"]
        story.descendants = story_data["descendants"]
        story.updated_at = datetime.utcnow()

    def process_item(self, source, item):
        if not is_story_item(item):
            logger.info("item is not a story object")
            return True

        story_id = item["id"]
        logger.info("processing story with id %s", story_id)
        story = Story.get_by_story_id(self._session, story_id)

        if story is None:
            story = self._create_story(item)
        else:
            self._update_story(story, item)

        # it is not the most optimal thing to save the story items one at a
        # time. However for the moment it will do.
        try:
            self._session.commit()
            logger.info("processed story with id %s", story.story_id)

            return True
        except SQLAlchemyError:
            self._session.rollback()
            logger.exception("failed to save story with story id %s", story_id)

            return False


class RabbitMQProcessor(object):
    def __init__(self):
        self._publisher = None

    def configure(self, config):
        logger.info("Configuring RabbitMQProcessor")

        if self._publisher is not None:
            try:
                self._publisher.close()
            except Exception:
                logger.exception("failed to disconnect from RabbitMQ")

        self._publisher = create_publisher_from_config(config)

    def job_started(self, job):
        logger.info("connecting to RabbitMQ")

        try:
            self._publisher.open()
        except Exception:
            logger.exception("failed to connect to RabbitMQ")

    def job_finished(self, job):
        logger.info("disconnecting from RabbitMQ")

        try:
            self._publisher.close()
        except Exception:
            logger.exception("failed to disconnect from RabbitMQ")

    def process_item(self, source, item):
        if not is_story_item(item):
            logger.info("item is not a story object")
            return True

        logger.info("publishing story with id %s", item["id"])

        self._publisher.publish_story(item)

        return True
