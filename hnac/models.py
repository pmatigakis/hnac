from urlparse import urlparse
from datetime import datetime
from uuid import uuid4

import pytz
from sqlalchemy import (Column, String, Integer, DateTime, ForeignKey,
                        BigInteger, Boolean)

from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from flask_login import UserMixin


Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(40), unique=True, nullable=False)

    stories = relationship("Story", back_populates="user")

    @classmethod
    def create(cls, session, username):
        user = cls(username=username)

        session.add(user)

        return user

    @classmethod
    def get_by_username(cls, session, username):
        return session.query(cls)\
                      .filter_by(username=username)\
                      .one_or_none()

    @classmethod
    def count(cls, session):
        return session.query(cls).count()


class Domain(Base):
    __tablename__ = "domains"

    id = Column(Integer, primary_key=True)
    domain = Column(String(256), unique=True, nullable=False)

    urls = relationship("Url", back_populates="domain")

    @classmethod
    def get_by_domain_name(cls, session, domain_name):
        return session.query(cls)\
                      .filter_by(domain=domain_name)\
                      .one_or_none()

    @classmethod
    def create(cls, session, domain_name):
        domain_object = cls(domain=domain_name)

        session.add(domain_object)

        return domain_object


class Url(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True)
    domain_id = Column(ForeignKey("domains.id"), nullable=False)
    url = Column(String(512), unique=True, nullable=False)

    domain = relationship("Domain", back_populates="urls")
    stories = relationship("Story", back_populates="url")

    @classmethod
    def get_by_url(cls, session, url):
        return session.query(cls)\
                      .filter_by(url=url)\
                      .one_or_none()

    @classmethod
    def create(cls, session, url):
        parsed_url = urlparse(url)
        domain_name = parsed_url.netloc

        domain_object = Domain.get_by_domain_name(session, domain_name)

        if not domain_object:
            domain_object = Domain.create(session, domain_name)

        url_object = cls(url=url, domain=domain_object)

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

    @classmethod
    def get_by_id(cls, session, story_id):
        return session.query(cls).filter(Story.id == story_id).one_or_none()

    @classmethod
    def create_from_dict(cls, session, story_data):
        user_object = User.get_by_username(session, story_data["by"])

        if not user_object:
            user_object = User.create(session, story_data["by"])

        url_object = Url.get_by_url(session, story_data["url"])

        if not url_object:
            url_object = Url.create(session, story_data["url"])

        created_at = datetime.fromtimestamp(story_data["time"], tz=pytz.UTC)

        story_object = cls(
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

    @classmethod
    def update_from_dict(cls, session, story_data):
        story = cls.get_by_id(session, story_data["id"])

        story.score = story_data["score"]
        story.comment_count = story_data["descendants"]
        story.updated_at = datetime.utcnow().replace(tzinfo=None)

        return story


class APIUser(Base, UserMixin):
    __tablename__ = "api_users"

    id = Column(Integer, nullable=False, primary_key=True)
    username = Column(String(40), nullable=False, unique=True)
    password = Column(String(256), nullable=False)
    jti = Column(String(32), nullable=False)
    registered_at = Column(DateTime(timezone=False), nullable=False)
    active = Column(Boolean, nullable=False)

    @classmethod
    def get_by_username(cls, session, username):
        return session.query(cls).filter_by(username=username).one_or_none()

    @classmethod
    def create(cls, session, username, password, active=True):
        user = cls(username=username,
                   password=generate_password_hash(password),
                   active=active,
                   registered_at=datetime.utcnow(),
                   jti=uuid4().hex)

        session.add(user)

        return user

    @classmethod
    def delete(cls, session, username):
        user = cls.get_by_username(session, username)

        if user:
            session.delete(user)

        return user

    @classmethod
    def authenticate(cls, session, username, password):
        user = cls.get_by_username(session, username)

        if not user:
            return None

        if not check_password_hash(user.password, password):
            return None

        return user

    @property
    def is_active(self):
        return self.active

    def change_password(self, password):
        self.password = generate_password_hash(password)

        self.jti = uuid4().hex
