from abc import ABCMeta, abstractmethod
import json

import arrow


class MessageBase(metaclass=ABCMeta):
    """RabbitMQ message base"""

    @abstractmethod
    def dumps(self):
        """Dump the mesage into a string

        :rtype: str
        :return: the serialized message
        """
        pass


class JsonDocumentMessageBase(MessageBase, metaclass=ABCMeta):
    """JSON based message"""

    @abstractmethod
    def to_json(self):
        """Dump the message into json compatible dictionary

        :rtype: dict
        :return: the dictionary with the message data
        """
        pass

    def dumps(self):
        json_data = self.to_json()
        return json.dumps(json_data)


class UrlDocumentMessage(JsonDocumentMessageBase):
    """Url document message"""

    def __init__(self, url):
        self.url = url
        self.source = "hackernews-api"
        self.created_at = arrow.utcnow()

    def to_json(self):
        return {
            "type": "url",
            "created_at": self.created_at.format('YYYY-MM-DD HH:mm:ss ZZ'),
            "created_at_timestamp": self.created_at.timestamp,
            "data": {
                "url": self.url
            },
            "meta": {
                "source": self.source,
                "retrieved_by": "hnac"
            }
        }


class StoryDocumentMessage(JsonDocumentMessageBase):
    """Hackernews story document message"""

    def __init__(self, story):
        self.story = story
        self.source = "hackernews-api"
        self.created_at = arrow.utcnow()

    def to_json(self):
        return {
            "type": "story",
            "data": self.story,
            "created_at": self.created_at.format('YYYY-MM-DD HH:mm:ss ZZ'),
            "created_at_timestamp": self.created_at.timestamp,
            "meta": {
                "source": self.source,
                "retrieved_by": "hnac"
            }
        }
