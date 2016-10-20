import os

from hnac.web.app import create_app

environment_type = os.getenv("HNAC_ENV_TYPE", "production")

settings_file = os.getenv("HNAC_SETTINGS")

if settings_file is None:
    print("The environment variable HNAC_SETTINGS is not set")
    exit(1)

app = create_app(environment_type, settings_file)
