from flask_restful import Resource, marshal_with, abort
from flask_uauth.decorators import authentication_required

from hnac.web.apis import models
from hnac.web.apis.arguments import url_stories_query_parser
from hnac.models import Url
from hnac.web.database import db


class UrlStories(Resource):
    @marshal_with(models.story)
    @authentication_required
    def get(self):
        args = url_stories_query_parser.parse_args()

        url = Url.get_by_url(db.session, args.url)
        if url is None:
            return abort(
                404,
                error="url doesn't exist",
                url=args.url
            )

        return [
            story.as_dict()
            for story in url.stories
        ]
