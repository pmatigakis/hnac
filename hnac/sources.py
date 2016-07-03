import logging
from time import time, sleep

from firebase import FirebaseApplication
from requests import RequestException


logger = logging.getLogger(__name__)


class HackernewsStories(object):
    def __init__(self, wait_time=1.0, backoff_time=5.0, abort_after=3):
        self.wait_time = wait_time
        self.backoff_time = backoff_time
        self.abort_after = abort_after

        self._last_request_time = 0.0

        api_endpoint = "https://hacker-news.firebaseio.com"

        self._firebase = FirebaseApplication(api_endpoint, None)

    def _fetch_item(self, item_id):
        logger.debug("Fetching item %d", item_id)

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
            except RequestException:
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

    def items(self):
        new_stories = self._get_new_stories()

        for story_id in new_stories:
            item_data = self._get_story_data(story_id) 

            yield item_data

            self._throttle()
