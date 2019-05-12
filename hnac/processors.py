from abc import ABCMeta, abstractmethod
import logging
from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError

from hnac.schemas import HackernewsStorySchema
from hnac.models import HackernewsUser, Url, Story, HackernewsStoryItem
from hnac.queues import create_publisher
from hnac.exceptions import ItemProcessingError
from hnac.messages import StoryDocumentMessage, UrlDocumentMessage


logger = logging.getLogger(__name__)


class Processor(object):
    """Base processor object"""

    __metaclass__ = ABCMeta

    @abstractmethod
    def process_item(self, source, item):
        """Process the given item

        :param Source source: the source that generated the object
        :param dict item: the hackernews item
        :rtype: boolean
        :return: True if the item has been processed without errors
        """
        pass

    def configure(self, config):
        """Configure the Processor implementation

        :param dict config: the processor configuration
        """
        pass

    def job_started(self, job):
        """Signal the Processor implementation that the job has started

        :param Job job: the job
        """
        pass

    def job_finished(self, job):
        """Signal the Processor implementation that the job has finished

        :param Job job: the job
        """
        pass


class DummyProcessor(Processor):
    def process_item(self, source, item):
        print(item)


class SQLAlchemyStorage(Processor):
    """Save the hackernews stories to a database using sqlalchemy"""

    def __init__(self, session):
        """Create a new SQLAlchemyStorage object

        :param Session session: the sqlalchemy Session object to use
        """
        self._session = session

    def _create_story(self, story_data):
        story_id = story_data.id

        logger.info("creating story object with story id %s", story_id)

        username = story_data.by
        user = HackernewsUser.get_or_create_by_username(
            session=self._session,
            username=username
        )

        url_object = Url.get_or_create_by_url(self._session, story_data.url)

        story = Story.create(
            session=self._session,
            url=url_object,
            user=user,
            story_id=story_id,
            title=story_data.title,
            score=story_data.score,
            time=story_data.time,
            descendants=story_data.descendants
        )

        return story

    def _update_story(self, story, story_data):
        logger.info("updating story object with story id %s", story.story_id)

        story.score = story_data.score
        story.descendants = story_data.descendants
        story.updated_at = datetime.utcnow()

    def process_item(self, source, item):
        if not isinstance(item, HackernewsStoryItem):
            logger.info("item is not a story object")
            return

        story_id = item.id
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
        except SQLAlchemyError:
            self._session.rollback()
            logger.exception("failed to save story with story id %s", story_id)

            raise ItemProcessingError("failed to save story to database")


class RabbitMQProcessorBase(Processor):
    """Base class for processor that use RabbitMQ"""

    __metaclass__ = ABCMeta

    def __init__(self):
        self._publisher = None

    def configure(self, config):
        logger.info("Configuring RabbitMQStoryProcessor")

        if self._publisher is not None:
            try:
                self._publisher.close()
            except Exception:
                logger.exception("failed to disconnect from RabbitMQ")

        self._publisher = self._create_publisher(config)

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

    @abstractmethod
    def _create_publisher(self, config):
        """Create the publisher object that this processor will use

        :param dict config: the configuration settings
        :rtype: RabbitMQPublisher
        :return: the publisher that this processor will use
        """
        pass

    @abstractmethod
    def _create_message(self, item):
        """Create a message to be transmitted using data from the hackernews
        item

        :param object item: the hackernews item
        :rtype: MessageBase
        :return: the message to transmit
        """
        pass

    def process_item(self, source, item):
        """Process the given item

        :param Source source: the source that returned this item
        :param object item: the hackernews item to process
        """
        message = self._create_message(item)
        self._publisher.publish_message(message)


class RabbitMQStoryProcessor(RabbitMQProcessorBase):
    """Processor that published the hackernews stories to a RabbitMQ server"""

    def _create_publisher(self, config):
        return create_publisher(
            host=config["RABBITMQ_STORY_PROCESSOR_HOST"],
            port=config.get("RABBITMQ_STORY_PROCESSOR_PORT"),
            username=config.get("RABBITMQ_STORY_PROCESSOR_USERNAME"),
            password=config.get("RABBITMQ_STORY_PROCESSOR_PASSWORD"),
            exchange=config["RABBITMQ_STORY_PROCESSOR_EXCHANGE"],
            routing_key=config["RABBITMQ_STORY_PROCESSOR_ROUTING_KEY"],
            exchange_type=config["RABBITMQ_STORY_PROCESSOR_EXCHANGE_TYPE"],
            durable=config["RABBITMQ_STORY_PROCESSOR_EXCHANGE_DURABLE"],
            auto_delete=config["RABBITMQ_STORY_PROCESSOR_EXCHANGE_AUTO_DELETE"]
        )

    def _create_message(self, item):
        if not isinstance(item, HackernewsStoryItem):
            logger.info("item is not a story object")
            return

        logger.info("publishing story with id %s", item.id)

        schema = HackernewsStorySchema()
        serialization_result = schema.dump(item)
        if serialization_result.errors:
            logger.warning(
                "failed to serialize story: errors(%s)",
                serialization_result.errors
            )

            raise ItemProcessingError("failed to serialize story data")

        return StoryDocumentMessage(
            story=serialization_result.data
        )


class RabbitMQURLProcessor(RabbitMQProcessorBase):
    """Processor that published the urls of hackernews stories to a RabbitMQ
    server"""

    def _create_publisher(self, config):
        return create_publisher(
            host=config["RABBITMQ_URL_PROCESSOR_HOST"],
            port=config.get("RABBITMQ_URL_PROCESSOR_PORT"),
            username=config.get("RABBITMQ_URL_PROCESSOR_USERNAME"),
            password=config.get("RABBITMQ_URL_PROCESSOR_PASSWORD"),
            exchange=config["RABBITMQ_URL_PROCESSOR_EXCHANGE"],
            routing_key=config["RABBITMQ_URL_PROCESSOR_ROUTING_KEY"],
            exchange_type=config["RABBITMQ_URL_PROCESSOR_EXCHANGE_TYPE"],
            durable=config["RABBITMQ_URL_PROCESSOR_EXCHANGE_DURABLE"],
            auto_delete=config["RABBITMQ_URL_PROCESSOR_EXCHANGE_AUTO_DELETE"]
        )

    def _create_message(self, item):
        if not isinstance(item, HackernewsStoryItem):
            logger.info("item is not a story object")
            return

        if item.url is None:
            logger.info("story with id %s doesn't contain a url", item.id)
            raise ItemProcessingError("story doesn't contain a url")

        return UrlDocumentMessage(item.url)


class Processors(object):
    """Processor collection object"""

    def __init__(self):
        self._processors = []

    @property
    def count(self):
        """Return the number of processors

        :rtype: int
        :return: the number of processors
        """
        return len(self._processors)

    def get(self, index):
        """Get a processor by index

        :param int index: the processor index
        :rtype: Processor
        :return: the processor
        """
        return self._processors[index]

    def remove(self, index):
        """Remove a processor by index

        :param int index: the processor index
        """
        self._processors.pop(index)

    def add(self, processor):
        """Add a processor to the collection

        :param Processor processor: a processor object
        """
        self._processors.append(processor)

    def add_multiple(self, processors):
        """Add multiple processors to the collection

        :param list[Processor] processors: a list of processor objects
        """
        self._processors.extend(processors)

    def configure_all(self, config):
        """Configure the processors

        :param dict config: the configuration dictionary
        """
        for processor in self._processors:
            processor.configure(config)

    def job_started(self, job):
        """Notify the processors that a job started

        :param Job job: the job that was started
        """
        for processor in self._processors:
            processor.job_started(job)

    def job_finished(self, job):
        """Notify the processors that the job has finished

        :param Job job: the finished job
        """
        for processor in self._processors:
            processor.job_finished(job)

    def process_item(self, source, item):
        """Use the processors to process the given item

        :param Source source: the source that generated the item
        :param HackernewsStoryItem item: the item to process
        """
        for processor in self._processors:
            try:
                processor.process_item(source, item)
            except ItemProcessingError:
                logger.info("processor %s failed to process item",
                            type(processor))
            except Exception:
                logger.exception("processor failed to process item")
