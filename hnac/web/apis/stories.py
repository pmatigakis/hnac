from flask_restplus import Resource, Namespace

from hnac.web import session
from hnac.models import Story
from hnac.web.apis.arguments import story_list_query_parser
from hnac.queries.stories import fetch_stories
from hnac.web.apis.models import brief_story, story as story_model


api = Namespace("stories")
api.models[brief_story.name] = brief_story
api.models[story_model.name] = story_model


@api.route("/")
class LatestStories(Resource):
    @api.expect(story_list_query_parser)
    @api.marshal_list_with(brief_story)
    def get(self):
        args = story_list_query_parser.parse_args()

        stories = fetch_stories(session, args.limit, args.offset)

        stories = [{"id": story.id,
                    "title": story.title,
                    "url": story.url.url}
                   for story in stories]

        return stories


@api.route("/<int:story_id>")
class StoryDetails(Resource):
    @api.marshal_with(story_model)
    def get(self, story_id):
        story = session.query(Story).get(story_id)

        if not story:
            return {"error": "story doesn't exist", "story_id": story_id}

        story_details = {
            "id": story_id,
            "title": story.title,
            "url": story.url.url,
            "username": story.user.username,
            "created_at": story.created_at,
            "score": story.score,
            "comment_count": story.comment_count
        }

        return story_details
