from distutils.util import strtobool
import os

from dotenv import load_dotenv


load_dotenv(dotenv_path=os.getenv("CONFIGURATION_FILE"))


SECRET_KEY = os.environ["SECRET"]
TESTING = bool(strtobool(os.getenv("TESTING", "False")))
DEBUG = bool(strtobool(os.getenv("DEBUG", "False")))

SQLALCHEMY_DATABASE_URI = os.environ["SQLALCHEMY_DATABASE_URI"]

CRAWLER_WAIT_TIME = float(os.getenv("CRAWLER_WAIT_TIME", 1.0))
CRAWLER_BACKOFF_TIME = float(os.getenv("CRAWLER_BACKOFF_TIME", 1.0))
CRAWLER_ABORT_AFTER = int(os.getenv("CRAWLER_ABORT_AFTER", 3))

API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("API_PORT", 5000))

PROPAGATE_EXCEPTIONS = bool(
    strtobool(os.getenv("PROPAGATE_EXCEPTIONS", "True"))
)

RABBITMQ_PROCESSOR = os.getenv("RABBITMQ_PROCESSOR")
RABBITMQ_PROCESSOR_EXCHANGE = os.getenv(
    "RABBITMQ_PROCESSOR_EXCHANGE",
    "stories"
)
RABBITMQ_PROCESSOR_EXCHANGE_TYPE = os.getenv(
    "RABBITMQ_PROCESSOR_EXCHANGE_TYPE",
    "topic"
)
RABBITMQ_PROCESSOR_EXCHANGE_DURABLE = bool(
    strtobool(os.getenv("RABBITMQ_PROCESSOR_EXCHANGE_DURABLE", "True"))
)
RABBITMQ_PROCESSOR_EXCHANGE_AUTO_DELETE = bool(
    strtobool(os.getenv("RABBITMQ_PROCESSOR_EXCHANGE_AUTO_DELETE", "False"))
)
RABBITMQ_PROCESSOR_ROUTING_KEY = os.getenv(
    "RABBITMQ_PROCESSOR_ROUTING_KEY",
    "stories.new"
)

PROCESSORS = []
if RABBITMQ_PROCESSOR:
    PROCESSORS.append("hnac.processors.RabbitMQProcessor")

STORY_DUMP_BATCH_SIZE = int(os.getenv("STORY_DUMP_BATCH_SIZE", 300))

if not TESTING:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': "%(asctime)s %(levelname)s [%(process)d:%(thread)d] %(name)s [%(pathname)s:%(funcName)s:%(lineno)d] %(message)s"
            }
        },
        'handlers': {
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose'
            }
        },
        'loggers': {
            'hnac': {
                'handlers': ['console'],
                'propagate': True
            }
        },
        "root": {
            'level': 'INFO',
        }
    }
