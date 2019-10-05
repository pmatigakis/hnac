import os
from os import path

from hnac.web.app import create_app


environment_type = os.getenv("HNAC_ENVIRONMENT_TYPE", "production")
settings_file = path.join(os.getcwd(), "settings.py")
app = create_app(environment_type, settings_file)
