from urlparse import urlparse
from datetime import datetime

import pytz
from sqlalchemy import (Column, String, Integer, DateTime, ForeignKey,
                        BigInteger)

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(40), unique=True, nullable=False)

    stories = relationship("Story", back_populates="user")

    @staticmethod
    def create(session, username):
        user = User(username=username)

        session.add(user)

        return user

    @staticmethod
    def get_by_username(session, username):
        return session.query(User)\
                      .filter_by(username=username)\
                      .one_or_none()

    @staticmethod
    def count(session):
        return session.query(User).count()


class Domain(Base):
    __tablename__ = "domains"

    id = Column(Integer, primary_key=True)
    domain = Column(String(256), unique=True, nullable=False)

    urls = relationship("Url", back_populates="domain")

    @staticmethod
    def get_by_domain_name(session, domain_name):
        return session.query(Domain)\
                      .filter_by(domain=domain_name)\
                      .one_or_none()

    @staticmethod
    def create(session, domain_name):
        domain_object = Domain(domain=domain_name)

        session.add(domain_object)

        return domain_object


class Url(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True)
    domain_id = Column(ForeignKey("domains.id"), nullable=False)
    url = Column(String(512), unique=True, nullable=False)

    domain = relationship("Domain", back_populates="urls")
    stories = relationship("Story", back_populates="url")

    @staticmethod
    def get_by_url(session, url):
        return session.query(Url)\
                      .filter_by(url=url)\
                      .one_or_none()

    @staticmethod
    def create(session, url):
        parsed_url = urlparse(url)
        domain_name = parsed_url.netloc

        domain_object = Domain.get_by_domain_name(session, domain_name)

        if not domain_object:
            domain_object = Domain.create(session, domain_name)

        url_object = Url(url=url, domain=domain_object)

        session.add(url_object)

        return url_object


class Story(Base):
    __tablename__ = "stories"

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    url_id = Column(ForeignKey("urls.id"), nullable=False)
    user_id = Column(ForeignKey("users.id"), nullable=False)
    score = Column(Integer, nullable=False)
    comment_count = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=False), nullable=False)
    added_at = Column(DateTime(timezone=False), nullable=False)
    updated_at = Column(DateTime(timezone=False))
    created_at_timestamp = Column(BigInteger, nullable=False, index=True)

    user = relationship("User", back_populates="stories")
    url = relationship("Url", back_populates="stories")

    @staticmethod
    def get_by_id(session, story_id):
        return session.query(Story).filter(Story.id == story_id).one_or_none()

    @staticmethod
    def create_from_dict(session, story_data):
        user_object = User.get_by_username(session, story_data["by"])

        if not user_object:
            user_object = User.create(session, story_data["by"])

        url_object = Url.get_by_url(session, story_data["url"])

        if not url_object:
            url_object = Url.create(session, story_data["url"])

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

        return story_object

    @staticmethod
    def update_from_dict(session, story_data):
        story = Story.get_by_id(session, story_data["id"])

        story.score = story_data["score"]
        story.comment_count = story_data["descendants"]
        story.updated_at = datetime.utcnow().replace(tzinfo=None)

        return story
