from sqlalchemy import create_engine
from flask_script import Command
from flask import current_app

from hnac.models import Base


class CreateDatabase(Command):
    """Create the hackernews crawler database"""

    def run(self):
        config = current_app.config

        engine = create_engine(config["DB"])
        Base.metadata.create_all(engine)
