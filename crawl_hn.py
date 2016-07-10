import logging 
from ConfigParser import ConfigParser

from hnac.jobs import HackernewsStoryDownloader


config = ConfigParser()

config.read("hnac.ini")

log_format = '%(asctime)s %(name)s %(levelname)s %(message)s' 

formatter = logging.Formatter(log_format)

logger = logging.getLogger()

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("hnac.log")
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)

logger.addHandler(console_handler)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)

job = HackernewsStoryDownloader(config)

job.run()
