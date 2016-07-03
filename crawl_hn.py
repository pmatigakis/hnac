import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from hnac.models import Base
from hnac.crawlers import Crawler
from hnac.sources import HackernewsStories
from hnac.processors import SQLAlchemyStorage
 
logger = logging.getLogger()
handler = logging.StreamHandler()

formatter = logging.Formatter(
    '%(asctime)s %(name)s %(levelname)s %(message)s')

handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

engine = create_engine("mysql://root:root@localhost/hnac?charset=utf8")

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)

session = Session()

processor = SQLAlchemyStorage(session)

source = HackernewsStories()

crawler = Crawler(source, processor)

try:
    crawler.run()
finally:
    session.close()
