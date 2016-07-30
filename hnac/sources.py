from abc import ABCMeta, abstractmethod
import logging
from time import time, sleep

from firebase import FirebaseApplication
from requests import RequestException

from hnac.schemas import is_story_item, HackernewsStorySchema


logger = logging.getLogger(__name__)


class Source(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def has_more_items(self):
        pass

    @abstractmethod
    def get_next_item(self):
        pass

    def configure(self, config):
        pass

    def job_started(self, job):
        pass

    def job_finished(self, job):
        pass


class HackernewsStories(Source):
    def __init__(self):
        super(HackernewsStories, self).__init__()

        self.wait_time = 1.0
        self.backoff_time = 5.0
        self.abort_after = 3

        self._last_request_time = 0.0

        api_endpoint = "https://hacker-news.firebaseio.com"

        self._firebase = FirebaseApplication(api_endpoint, None)

        self._story_ids = None

    def configure(self, config):
        if "HNAC_CRAWLER_WAIT_TIME" in config:
            self.wait_time = config["HNAC_CRAWLER_WAIT_TIME"]

        if "HNAC_CRAWLER_BACKOFF_TIME" in config:
            self.backoff_time = config["HNAC_CRAWLER_BACKOFF_TIME"]

        if "HNAC_CRAWLER_ABORT_AFTER" in config:
            self.abort_after = config["HNAC_CRAWLER_ABORT_AFTER"]

    def _fetch_item(self, item_id):
        logger.debug("Fetching hackernews item %d", item_id)

        self._last_request_time = time()

        return self._firebase.get("/v0/item", item_id)

    def _throttle(self):
        time_diff = time() - self._last_request_time

        sleep_for = self.wait_time - time_diff

        if sleep_for > 0.0:
            logger.debug("sleeping due to throttling for %f seconds",
                         sleep_for)

            sleep(sleep_for)

    def _get_new_stories(self):
        failure_count = 0

        while True:
            try:
                return self._firebase.get("/v0/newstories", None)
            except RequestException as e:
                print e
                logger.exception("Failed to fetch new story ids")

                failure_count += 1
                if failure_count > self.abort_after:
                    raise

                sleep(self.backoff_time)

    def _get_story_data(self, story_id):
        failure_count = 0

        while True:
            try:
                return self._fetch_item(story_id)
            except RequestException:
                logger.exception("Failed to fetch story %d", story_id)

                failure_count += 1
                if failure_count > self.abort_after:
                    raise

                sleep(self.backoff_time)

    def has_more_items(self):
        if self._story_ids is None:
            self._story_ids = self._get_new_stories()

        return len(self._story_ids) > 0

    def get_next_item(self):
        if self._story_ids:
            story_id = self._story_ids.pop()

            self._throttle()

            story_data = self._get_story_data(story_id)

            if is_story_item(story_data):
                schema = HackernewsStorySchema()

                story = schema.load(story_data)

                if not story.errors:
                    return story

                for field in story.errors:
                    for error_message in story.errors[field]:
                        logger.warning("story %d error: %s",
                                       story_id, error_message)

        return None
