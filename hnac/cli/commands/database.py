import os.path
import pkg_resources
import json

from sqlalchemy import create_engine
from flask_script import Command
from flask import current_app
from couchdb import Server

from hnac.models import Base


class CreateDatabase(Command):
    """Create the hackernews crawler database"""

    def run(self):
        config = current_app.config

        engine = create_engine(config["DB"])
        Base.metadata.create_all(engine)

        server = Server(config["COUCHDB_SERVER"])
        db = server[config["COUCHDB_DATABASE"]]

        stories_view_code = pkg_resources.resource_string(
            "hnac", os.path.join("couchdb", "views.json"))
        stories_view = json.loads(stories_view_code.decode("utf8"))

        existing_stories_view = db.get("_design/stories")
        if existing_stories_view is not None:
            stories_view["_rev"] = existing_stories_view["_rev"]

        db["_design/stories"] = stories_view
