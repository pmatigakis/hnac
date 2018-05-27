import logging

from flask_restful import Resource, marshal_with, abort
from flask_jwt import jwt_required

from hnac.web.apis.arguments import story_list_query_parser
from hnac.web.apis import models
from hnac.web import session
from hnac.models import Story


logger = logging.getLogger(__name__)


class Stories(Resource):
    @marshal_with(models.story)
    @jwt_required()
    def get(self):
        args = story_list_query_parser.parse_args()

        logger.info(
            "retrieving stories offset=%s limit=%s", args.offset, args.limit)

        stories = Story.get_stories(session, args.offset, args.limit)

        return [
            story.as_dict()
            for story in stories
        ]


class StoryDetails(Resource):
    @marshal_with(models.story)
    @jwt_required()
    def get(self, story_id):
        logger.info("retrieving story with id %s", story_id)

        story = Story.get_by_story_id(session, story_id)

        if not story:
            logger.warning("story with id %s doesn't exist", story_id)

            abort(
                404,
                error="story doesn't exist",
                story_id=story_id
            )

        return story.as_dict()
