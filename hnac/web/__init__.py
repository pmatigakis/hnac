from sqlalchemy.orm import sessionmaker, scoped_session
from flask_restful import Api

SessionMaker = sessionmaker()

session = scoped_session(SessionMaker)

api = Api()
