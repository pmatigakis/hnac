from datetime import datetime
from uuid import uuid4
from collections import namedtuple

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask_uauth.mixins import TokenMixin

from hnac.web.database import db
from hnac.web.queries import operations
from hnac.exceptions import UnsupportedSearchOperation


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(
        db.Integer, db.Sequence("users_id_seq"), nullable=False,
        primary_key=True)
    username = db.Column(db.String(40), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    registered_at = db.Column(db.DateTime(timezone=False), nullable=False)
    active = db.Column(db.Boolean, nullable=False)

    @classmethod
    def get_by_username(cls, session, username):
        return session.query(cls).filter_by(username=username).one_or_none()

    @classmethod
    def create(cls, session, username, password, active=True):
        user = cls(username=username,
                   password=generate_password_hash(password),
                   active=active,
                   registered_at=datetime.utcnow())

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


class Token(db.Model, TokenMixin):
    __tablename__ = "tokens"

    id = db.Column(
        db.Integer, db.Sequence("tokens_id_seq"), nullable=False,
        primary_key=True)
    name = db.Column(db.String(40), nullable=False, unique=True)
    value = db.Column(db.String(32), nullable=False, unique=True)
    active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime(timezone=False), nullable=False)

    def is_active(self):
        return self.active

    @classmethod
    def create(cls, session, name):
        token = cls(
            name=name,
            value=uuid4().hex,
            created_at=datetime.utcnow(),
            active=True
        )

        session.add(token)

        return token

    @classmethod
    def get_by_value(cls, session, value):
        return session.query(cls).filter_by(value=value).one_or_none()

    @classmethod
    def get_by_name(cls, session, name):
        return session.query(cls).filter_by(name=name).one_or_none()

    @classmethod
    def all(cls, session):
        return session.query(cls).order_by(cls.name).all()

    def delete(self, session):
        session.delete(self)


class Report(db.Model):
    __tablename__ = "reports"

    id = db.Column(db.Integer, db.Sequence("reports_id_seq"),
                   nullable=False, primary_key=True)

    job_id = db.Column(db.String(32), nullable=False)
    started_at = db.Column(db.DateTime(timezone=False), nullable=False)
    completed_at = db.Column(db.DateTime(timezone=False), nullable=False)
    failed = db.Column(db.Boolean, nullable=False, default=False)
    num_processed_items = db.Column(db.Integer, nullable=False)

    @classmethod
    def save_report(cls, session, job_execution_result):
        report_object = cls(
            job_id=job_execution_result.job.id,
            started_at=job_execution_result.start_time,
            completed_at=job_execution_result.end_time,
            failed=job_execution_result.failed,
            num_processed_items=job_execution_result.processed_item_count
        )

        session.add(report_object)

        return report_object

    @classmethod
    def get_latest(cls, session, count=10):
        return session.query(cls)\
                      .order_by(db.desc(cls.started_at))\
                      .limit(count).all()


class HackernewsUser(db.Model):
    __tablename__ = "hackernews_users"

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    username = db.Column(db.String(40), nullable=False, unique=True)
    created_at = db.Column(db.DateTime(timezone=False), nullable=False)

    @classmethod
    def create(cls, session, username):
        user = cls(
            username=username,
            created_at=datetime.utcnow()
        )

        session.add(user)

        return user

    @classmethod
    def get_by_username(cls, session, username):
        return session.query(cls).filter_by(username=username).one_or_none()

    @classmethod
    def get_or_create_by_username(cls, session, username):
        user = cls.get_by_username(session, username)
        if user is None:
            user = cls.create(session, username)
            session.add(user)

        return user


class Url(db.Model):
    __tablename__ = "urls"

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    url = db.Column(db.String(2048), nullable=False, unique=True)
    created_at = db.Column(db.DateTime(timezone=False))

    @classmethod
    def create(cls, session, url):
        url_object = cls(
            url=url,
            created_at=datetime.utcnow()
        )

        session.add(url_object)

        return url_object

    @classmethod
    def get_by_url(cls, session, url):
        return session.query(cls).filter_by(url=url).one_or_none()

    @classmethod
    def get_or_create_by_url(cls, session, url):
        url_object = cls.get_by_url(session, url)
        if url_object is None:
            url_object = Url.create(session, url)
            session.add(url_object)

        return url_object


class Story(db.Model):
    __tablename__ = "stories"

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    story_id = db.Column(db.Integer, nullable=False, unique=True)
    hackernews_user_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "hackernews_users.id",
            ondelete="CASCADE",
            onupdate="CASCADE"
        ),
        nullable=False
    )
    url_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "urls.id",
            ondelete="CASCADE",
            onupdate="CASCADE"
        ),
        nullable=False
    )
    title = db.Column(db.String(512), nullable=False)
    score = db.Column(db.Integer, nullable=False, index=True)
    time = db.Column(db.Integer, nullable=False, index=True)
    descendants = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone=False), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=False), nullable=False)

    hackernews_user = db.relationship("HackernewsUser")
    url = db.relationship("Url")

    @classmethod
    def create(cls, session, user, url, story_id, title, score, time,
               descendants):

        created_at = datetime.utcnow()

        story = cls(
            hackernews_user=user,
            url=url,
            story_id=story_id,
            title=title,
            score=score,
            time=time,
            descendants=descendants,
            created_at=created_at,
            updated_at=created_at
        )

        session.add(story)

        return story

    @classmethod
    def get_by_story_id(cls, session, story_id):
        return session.query(cls).filter_by(story_id=story_id).one_or_none()

    @classmethod
    def count(cls, session):
        return session.query(cls).count()

    @classmethod
    def get_latest(cls, session, count=20):
        return session.query(cls).order_by(db.desc(cls.time)).limit(count)

    @classmethod
    def get_stories(cls, session, offset=0, limit=500, order_by=None,
                    sort_desc=False):
        order_by = order_by or cls.id
        if sort_desc:
            order_by = db.desc(order_by)

        return session.query(cls) \
                      .order_by(order_by) \
                      .offset(offset) \
                      .limit(limit) \
                      .all()

    @classmethod
    def search(cls, session, criteria, offset=0, limit=500, order_by=None,
               sort_desc=False):
        supported_operations = [
            operations.EQ, operations.LT, operations.LTE, operations.GT,
            operations.GTE
        ]

        argument_mapping = {
            "username": HackernewsUser.username,
            "url": Url.url,
            "score": Story.score,
            "story_id": Story.story_id,
            "time": Story.time
        }

        query_object = session.query(Story)
        query_object = query_object.join(HackernewsUser)
        query_object = query_object.join(Url)

        for variable, operation, value in criteria:
            if (operation not in supported_operations or
                    variable not in argument_mapping):
                raise UnsupportedSearchOperation(variable, operation)

            field = argument_mapping.get(variable) or getattr(Story, variable)

            query_object = query_object.filter(
                operations.OPERATIONS[operation](field, value))

        order_by = order_by or Story.id
        if sort_desc:
            order_by = db.desc(order_by)

        query_object = query_object.order_by(order_by)
        query_object = query_object.limit(limit)
        query_object = query_object.offset(offset)

        return query_object.all()

    def as_dict(self):
        return {
            "id": self.story_id,
            "title": self.title,
            "url": self.url.url,
            "time": self.time,
            "by": self.hackernews_user.username,
            "score": self.score,
            "descendants": self.descendants
        }


HackernewsStoryItem = namedtuple(
    "HackernewsStoryItem",
    ["id", "type", "by", "descendants", "score", "time", "title", "url"]
)
