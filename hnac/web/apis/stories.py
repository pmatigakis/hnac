import logging

from flask_restful import Resource, marshal_with, abort
from flask_uauth.decorators import authentication_required

from hnac.web.apis.arguments import story_list_query_parser
from hnac.web.apis import models
from hnac.web.database import db
from hnac.models import Story


logger = logging.getLogger(__name__)


class Stories(Resource):
    @marshal_with(models.story)
    @authentication_required
    def get(self):
        args = story_list_query_parser.parse_args()

        logger.info(
            "retrieving stories offset=%s limit=%s", args.offset, args.limit)

        order_by_mappings = {
            "id": Story.story_id,
            "time": Story.time,
            "score": Story.score
        }

        stories = Story.get_stories(
            session=db.session,
            offset=args.offset,
            limit=args.limit,
            order_by=order_by_mappings[args.order_by],
            sort_desc=args.desc
        )

        return [
            story.as_dict()
            for story in stories
        ]


class StoryDetails(Resource):
    @marshal_with(models.story)
    @authentication_required
    def get(self, story_id):
        logger.info("retrieving story with id %s", story_id)

        story = Story.get_by_story_id(db.session, story_id)

        if not story:
            logger.warning("story with id %s doesn't exist", story_id)

            abort(
                404,
                error="story doesn't exist",
                story_id=story_id
            )

        return story.as_dict()
