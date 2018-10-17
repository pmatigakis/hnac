from datetime import timedelta
import json


from flask_script import Command, Option
from flask import current_app


from hnac.web.database import db
from hnac.models import Story
from hnac.helpers import open_output, current_date, current_date_with_timedelta
from hnac.cli.datatypes import date_string


class DumpStories(Command):
    """Dump the stories in the given time period"""

    option_list = (
        Option("--from", dest="from_date",
               default=current_date(), type=date_string),
        Option("--to", dest="to_date",
               default=current_date_with_timedelta(timedelta(days=1)),
               type=date_string),
        Option("--output")
    )

    def run(self, from_date, to_date, output):
        with open_output(output) as f_out:
            for story in Story.yield_in_period(
                    db.session, from_date, to_date,
                    current_app.config["STORY_DUMP_BATCH_SIZE"]):
                f_out.write("{}\n".format((json.dumps(story.as_dict()))))
