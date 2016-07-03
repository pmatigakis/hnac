import logging

from hnac.queries.stories import save_or_update_story


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

    def process_item(self, item_data):
        if not is_story_item(item_data):
            logger.debug("item is not a story object")
            return

        try:
            save_or_update_story(self._session, item_data)
        except:
            logger.error("failed to save or update story %d", item_data["id"])
