from abc import ABCMeta, abstractmethod
import logging
from time import time, sleep
from urllib.parse import urljoin

from marshmallow import ValidationError
import requests

from hnac.schemas import is_story_item, HackernewsStorySchema
from hnac.exceptions import HnacError


logger = logging.getLogger(__name__)


class SourceError(HnacError):
    pass


class RetryCountExceeded(SourceError):
    pass


class Source(object):
    """Base class for all hackernews item source objects"""

    __metaclass__ = ABCMeta

    @abstractmethod
    def items(self):
        """Retrieve the hackernews items

        :rtype: Iterable
        :return: a generator that return the hackernews items
        """
        pass

    def configure(self, config):
        """Configure the Source object

        :param dict config: the object configuration
        """
        pass

    def job_started(self, job):
        """Signal the source implementation that the job has started

        :param Job job: the job
        """
        pass

    def job_finished(self, job):
        """Signal the Source implementation that the job has finished

        :param Job job: the job
        """
        pass


class HackernewsStories(Source):
    """Hackernews source"""

    def __init__(self,
                 hackernews_api_url="https://hacker-news.firebaseio.com"):
        super(HackernewsStories, self).__init__()

        self.wait_time = 1.0
        self.backoff_time = 5.0
        self.abort_after = 3
        self.request_timeout = 5

        self._last_request_time = 0.0
        self._hackernews_api_url = hackernews_api_url
        self._story_ids = None

    def configure(self, config):
        if "CRAWLER_WAIT_TIME" in config:
            self.wait_time = config["CRAWLER_WAIT_TIME"]

        if "CRAWLER_BACKOFF_TIME" in config:
            self.backoff_time = config["CRAWLER_BACKOFF_TIME"]

        if "CRAWLER_ABORT_AFTER" in config:
            self.abort_after = config["CRAWLER_ABORT_AFTER"]

    def _throttle(self):
        time_diff = time() - self._last_request_time

        sleep_for = self.wait_time - time_diff

        if sleep_for > 0.0:
            logger.info("sleeping due to throttling for %f seconds", sleep_for)
            sleep(sleep_for)

    def _execute_new_stories_request(self):
        new_stories_url = urljoin(
            self._hackernews_api_url, "/v0/newstories.json")
        response = requests.get(new_stories_url, timeout=self.request_timeout)

        return response.json()

    def _get_new_stories(self):
        failure_count = 0

        while True:
            try:
                return self._execute_new_stories_request()
            except requests.RequestException as e:
                logger.exception("Failed to fetch new story ids")

                failure_count += 1
                if failure_count > self.abort_after:
                    logger.error(
                        "maximum number of attempts to retrieve new stories "
                        "has been reached")
                    raise RetryCountExceeded() from e

                sleep(self.backoff_time)

    def _get_story_data(self, story_id):
        logger.info("Fetching hackernews item %d", story_id)

        failure_count = 0

        while True:
            self._last_request_time = time()
            item_url = urljoin(
                self._hackernews_api_url, f"/v0/item/{story_id}.json")

            try:
                response = requests.get(item_url, timeout=self.request_timeout)

                return response.json()
            except requests.RequestException as e:
                logger.exception("Failed to fetch story %d", story_id)

                failure_count += 1
                if failure_count > self.abort_after:
                    logger.error(
                        "maximum number of attempts to retrieve story data "
                        "has been reached: story_id(%s)", story_id)
                    raise RetryCountExceeded() from e

                sleep(self.backoff_time)

    def items(self):
        story_ids = self._get_new_stories()

        for story_id in story_ids:
            self._throttle()
            story_data = self._get_story_data(story_id)

            if not is_story_item(story_data):
                logger.warning("Hackernews item with id %d is not a story",
                               story_id)
                continue

            schema = HackernewsStorySchema()
            try:
                story = schema.load(story_data)
            except ValidationError as e:
                logger.warning(
                    "failed to deserialize story item: error(%s)", e)
                continue

            yield story
