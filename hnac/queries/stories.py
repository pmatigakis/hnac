import logging
from datetime import datetime
from urlparse import urlparse

import pytz
from sqlalchemy.exc import SQLAlchemyError

from hnac.models import Story, Url, Domain, User


logger = logging.getLogger(__name__)


def fetch_stories(session, limit=500, offset=0):
    stories = session.query(Story)\
                     .order_by(Story.created_at_timestamp.desc())\
                     .limit(limit)\
                     .offset(offset)

    return stories


def get_or_insert_domain(session, domain):
    domain_object = session.query(Domain)\
                           .filter_by(domain=domain)\
                           .one_or_none()

    if domain_object:
        return domain_object

    domain_object = Domain(domain=domain)

    session.add(domain_object)

    try:
        session.commit()
    except SQLAlchemyError:
        logger.exception("failed to add domain %s",
                         domain)

        raise

    return domain_object


def get_or_insert_user(session, username):
    user_object = session.query(User)\
                         .filter_by(username=username)\
                         .one_or_none()

    if user_object:
        return user_object

    user_object = User(username=username)

    session.add(user_object)

    try:
        session.commit()
    except SQLAlchemyError:
        logger.exception("failed to add user %s",
                         username)

        raise

    return user_object


def get_or_insert_url(session, url):
    url_object = session.query(Url).filter_by(url=url).one_or_none()

    if url_object:
        return url_object

    parsed_url = urlparse(url)

    domain_object = get_or_insert_domain(session, parsed_url.netloc)

    url_object = Url(url=url, domain=domain_object)

    session.add(url_object)

    try:
        session.commit()
    except SQLAlchemyError:
        logger.exception("Failed to add url %s",
                         url)

        raise

    return url_object


def save_story(session, story_data):
    logger.debug("inserting story %d", story_data["id"])

    user_object = get_or_insert_user(session, story_data["by"])

    url_object = get_or_insert_url(session, story_data["url"])

    created_at = datetime.fromtimestamp(story_data["time"], tz=pytz.UTC)

    story_object = Story(
        id=story_data["id"],
        title=story_data["title"],
        url=url_object,
        user=user_object,
        score=story_data["score"],
        comment_count=story_data["descendants"],
        created_at=created_at.replace(tzinfo=None),
        added_at=datetime.utcnow().replace(tzinfo=None),
        created_at_timestamp=story_data["time"]
    )

    session.add(story_object)

    try:
        session.commit()
    except SQLAlchemyError:
        logger.exception("Failed to add story %d",
                         story_data["id"])
        raise

    return story_object


def update_story(session, story, story_data):
    logger.debug("updating story %d", story.id)

    story.score = story_data["score"]
    story.comment_count = story_data["descendants"]
    story.updated_at = datetime.utcnow().replace(tzinfo=None)

    try:
        session.commit()
    except SQLAlchemyError:
        logger.exception("Failed to update story %d",
                         story_data["id"])

        raise


def save_or_update_story(session, story_data):
    story_object = session.query(Story)\
                          .get(story_data["id"])

    if not story_object:
        story_object = save_story(session, story_data)
    else:
        update_story(session, story_object, story_data)

    return story_object
