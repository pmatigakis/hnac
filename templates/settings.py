DEBUG = False

SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://$username:$password@localhost:5432/$db"

# settings for the RabbitMQ story processor
# RABBITMQ_STORY_PROCESSOR = "amqp://guest:guest@localhost:5672/%2F"
# RABBITMQ_STORY_PROCESSOR_EXCHANGE = "hackernews"
# RABBITMQ_STORY_PROCESSOR_EXCHANGE_TYPE = "topic"
# RABBITMQ_STORY_PROCESSOR_EXCHANGE_DURABLE = True
# RABBITMQ_STORY_PROCESSOR_EXCHANGE_AUTO_DELETE = False
# RABBITMQ_STORY_PROCESSOR_ROUTING_KEY = "stories.new"

PROCESSORS = [
    # uncomment the following line to enable the RabbitMQ story processor
    # "hnac.processors.RabbitMQProcessor",
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
