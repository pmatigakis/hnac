from datetime import datetime

from sqlalchemy import (Column, String, Integer, DateTime, Boolean, Sequence,
                        desc)

from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.ext.declarative import declarative_base
from flask_login import UserMixin


Base = declarative_base()


class User(Base, UserMixin):
    __tablename__ = "users"

    id = Column(
        Integer, Sequence("users_id_seq"), nullable=False, primary_key=True)
    username = Column(String(40), nullable=False, unique=True)
    password = Column(String(256), nullable=False)
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


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, Sequence("reports_id_seq"),
                nullable=False, primary_key=True)

    job_id = Column(String(32), nullable=False)
    started_at = Column(DateTime(timezone=False), nullable=False)
    completed_at = Column(DateTime(timezone=False), nullable=False)
    failed = Column(Boolean, nullable=False, default=False)
    num_processed_items = Column(Integer, nullable=False)

    @classmethod
    def save_report(cls, session, report):
        report_object = cls(
            job_id=report.job.id,
            started_at=report.start_time,
            completed_at=report.end_time,
            failed=report.job.failed,
            num_processed_items=report.job.processed_item_count
        )

        session.add(report_object)

        return report_object

    @classmethod
    def get_latest(cls, session, count=10):
        return session.query(cls)\
                      .order_by(desc(cls.started_at))\
                      .limit(count).all()
