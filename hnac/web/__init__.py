from sqlalchemy.orm import sessionmaker, scoped_session
from flask_jwt import JWT


SessionMaker = sessionmaker()

session = scoped_session(SessionMaker)

jwt = JWT()
