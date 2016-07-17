from os import path

from hnac.configuration import (create_configuration,
                                HNAC_API_SECTION,
                                HNAC_API_HOST,
                                HNAC_API_PORT,
                                HNAC_API_DEBUG)

from hnac.crawlers import create_hackernews_api_crawler_job
from hnac.web.app import create_app


def create_configuration_file():
    config = create_configuration()

    with open("hnac.ini", "w") as f:
        config.write(f)


def start_crawler():
    configuration_file_path = path.abspath("hnac.ini")
    
    if not path.exists(configuration_file_path):
        print("File hnac.ini doesn't exist")
        exit(1)
    elif not path.isfile(configuration_file_path):
        print("hnac.ini is not a file")
        exit(1)

    config = create_configuration()

    with open(configuration_file_path, "r") as f:
        config.readfp(f)

    job = create_hackernews_api_crawler_job(config)

    job.run()


def start_api_server():
    configuration_file_path = path.abspath("hnac.ini")

    if not path.exists(configuration_file_path):
        print("File hnac.ini doesn't exist")
        exit(1)
    elif not path.isfile(configuration_file_path):
        print("hnac.ini is not a file")
        exit(1)

    config = create_configuration()

    with open(configuration_file_path, "r") as f:
        config.readfp(f)

    app = create_app(config)

    host = config.get(HNAC_API_SECTION, HNAC_API_HOST)
    port = config.getint(HNAC_API_SECTION, HNAC_API_PORT)
    debug = config.getboolean(HNAC_API_SECTION, HNAC_API_DEBUG)

    app.run(host, port, debug)
