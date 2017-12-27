DEBUG = False

DB = "postgresql+psycopg2://username:password@localhost:5432/hnac"

# settings for the CouchDb processor
# COUCHDB_SERVER = "http://localhost:5984"
# COUCHDB_DATABASE = "hnac"

# settings for the RabbitMQ story processor
# RABBITMQ_STORY_PROCESSOR_HOST = "localhost"
# RABBITMQ_STORY_PROCESSOR_EXCHANGE = "hackernews"
# RABBITMQ_STORY_PROCESSOR_ROUTING_KEY = "stories"
# RABBITMQ_STORY_PROCESSOR_USERNAME = "guest"
# RABBITMQ_STORY_PROCESSOR_PASSWORD = "guest"

# settings for the RabbitMQ url processor
# RABBITMQ_URL_PROCESSOR_HOST = "localhost"
# RABBITMQ_URL_PROCESSOR_EXCHANGE = "hackernews"
# RABBITMQ_URL_PROCESSOR_ROUTING_KEY = "urls"
# RABBITMQ_URL_PROCESSOR_USERNAME = "guest"
# RABBITMQ_URL_PROCESSOR_PASSWORD = "guest"


PROCESSORS = [
    # uncomment the following line in order to enable the CouchDB storage
    # "hnac.processors.CouchDBStorage",

    # uncomment the following line to enable the RabbitMQ story processor
    # "hnac.processors.RabbitMQStoryProcessor",

    # uncomment the following line to enable the RabbitMQ url processor
    # "hnac.processors.RabbitMQURLProcessor"
]

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
