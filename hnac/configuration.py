from ConfigParser import ConfigParser

DEFAULT_LOG_FILENAME = "hnac.log"

HNAC_CRAWLER_SECTION = "hnac_crawler"
HNAC_CRAWLER_LOG_FILE = "file"
HNAC_CRAWLER_ENABLE_LOGGING = "enable_logging"
HNAC_CRAWLER_DEBUG = "debug"
HNAC_CRAWLER_LOG_FILE_SIZE = "filesize"
HNAC_CRAWLER_LOG_FILE_COUNT = "file_count"

HNAC_DB_SECTION = "database"
HNAC_DB = "db_uri"

HNAC_API_SECTION = "api"
HNAC_API_HOST = "host"
HNAC_API_PORT = "port"
HNAC_API_DEBUG = "debug"


def create_configuration():
    config = ConfigParser()

    config.add_section(HNAC_CRAWLER_SECTION)
    config.add_section(HNAC_DB_SECTION)
    config.add_section(HNAC_API_SECTION)

    config.set(
        HNAC_API_SECTION,
        HNAC_API_HOST,
        "0.0.0.0"
    )

    config.set(
        HNAC_API_SECTION,
        HNAC_API_PORT,
        "5000"
    )

    config.set(
        HNAC_API_SECTION,
        HNAC_API_DEBUG,
        "true"
    )

    config.set(
        HNAC_CRAWLER_SECTION,
        HNAC_CRAWLER_LOG_FILE_SIZE,
        str(2 ** 20)
    )

    config.set(
        HNAC_CRAWLER_SECTION,
        HNAC_CRAWLER_LOG_FILE_COUNT,
        str(5)
    )

    config.set(
        HNAC_CRAWLER_SECTION,
        HNAC_CRAWLER_LOG_FILE,
        DEFAULT_LOG_FILENAME
    )

    config.set(
        HNAC_CRAWLER_SECTION,
        HNAC_CRAWLER_ENABLE_LOGGING,
        "true"
    )

    config.set(
        HNAC_CRAWLER_SECTION,
        HNAC_CRAWLER_DEBUG,
        "true"
    )

    config.set(
        HNAC_DB_SECTION,
        HNAC_DB,
        "sqlite:///:memory:"
    )

    return config
