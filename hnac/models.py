from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, BigInteger

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(40), unique=True, nullable=False)

    stories = relationship("Story", back_populates="user")


class Domain(Base):
    __tablename__ = "domains"

    id = Column(Integer, primary_key=True)
    domain = Column(String(256), unique=True, nullable=False)

    urls = relationship("Url", back_populates="domain")


class Url(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True)
    domain_id = Column(ForeignKey("domains.id"), nullable=False)
    url = Column(String(512), unique=True, nullable=False)

    domain = relationship("Domain", back_populates="urls")
    stories = relationship("Story", back_populates="url")


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
