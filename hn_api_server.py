from hnac.web.app import create_app

from ConfigParser import ConfigParser

config = ConfigParser()

config.read("hnac.ini")

app = create_app(config)

app.run()
