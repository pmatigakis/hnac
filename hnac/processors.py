import logging
from urlparse import urlparse
from datetime import datetime

import pytz
from sqlalchemy.exc import SQLAlchemyError

from hnac.models import HackernewsStory, Url, Domain, HackernewsUser


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


class SQLAlchemyStorage(object):
    def __init__(self, session):
        self._session = session

    def _get_or_insert_user(self, username):
        user_object = self._session.query(HackernewsUser).filter_by(username=username).one_or_none()

        if user_object:
            return user_object

        user_object = HackernewsUser(username=username)

        self._session.add(user_object)

        try:
            self._session.commit()
        except SQLAlchemyError:
            logger.exception("failed to add user %s",
                             username)

            raise

        return user_object


    def _get_or_insert_domain(self, domain):
        domain_object = self._session.query(Domain).filter_by(domain=domain).one_or_none()

        if domain_object:
            return domain_object

        domain_object = Domain(domain=domain)

        self._session.add(domain_object)

        try:
            self._session.commit()
        except SQLAlchemyError:
            logger.exception("failed to add domain %s",
                             domain)

            raise

        return domain_object

    def _get_or_insert_url(self, url):
        url_object = self._session.query(Url).filter_by(url=url).one_or_none()

        if url_object:
            return url_object

        parsed_url = urlparse(url)

        domain_object = self._get_or_insert_domain(parsed_url.netloc)

        url_object = Url(url=url, domain=domain_object)

        self._session.add(url_object)

        try:
            self._session.commit()
        except SQLAlchemyError:
            logger.exception("Failed to add url %s",
                             url)

            raise

        return url_object

    def _insert_story(self, story_data):
        logger.debug("inserting story %d", story_data["id"])

        user_object = self._get_or_insert_user(story_data["by"])

        url_object = self._get_or_insert_url(story_data["url"])

        created_at = datetime.fromtimestamp(story_data["time"], tz=pytz.UTC)

        story_object = HackernewsStory(
            id=story_data["id"],
            title=story_data["title"],
            url=url_object,
            user=user_object,
            score=story_data["score"],
            comment_count=story_data["descendants"],
            created_at=created_at.replace(tzinfo=None),
            added_at=datetime.utcnow().replace(tzinfo=None)
        )        

        self._session.add(story_object)

        try:
            self._session.commit()
        except SQLAlchemyError:
            logger.exception("Failed to add story %d",
                             story_data["id"])
            raise

    def _update_story(self, story, story_data):
        logger.debug("updating story %d", story.id)

        story.score = story_data["score"]
        story.comment_count = story_data["descendants"]
        story.updated_at = datetime.utcnow().replace(tzinfo=None)

        try:
            self._session.commit()
        except SQLAlchemyError:
            logger.exception("Failed to update story %d",
                             story_data["id"])

            raise

    def process_item(self, item_data):
        story_object = self._session.query(HackernewsStory)\
                                    .get(item_data["id"])

        if not is_story_item(item_data):
            return

        if not story_object:
            self._insert_story(item_data)
        else:
            self._update_story(story_object, item_data)
