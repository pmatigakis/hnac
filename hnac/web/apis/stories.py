from flask import current_app
from flask_restful import Resource, marshal_with, abort
import couchdb
from flask_jwt import jwt_required

from hnac.web.apis.arguments import story_list_query_parser
from hnac.web.apis import models


class Stories(Resource):
    @marshal_with(models.story)
    @jwt_required()
    def get(self):
        args = story_list_query_parser.parse_args()

        config = current_app.config

        server = couchdb.Server(config["HNAC_COUCHDB_SERVER"])
        db = server[config["HNAC_COUCHDB_DATABASE"]]

        stories = []

        for story in db.view("_all_docs", limit=args.limit,
                             include_docs=True, descending=True,
                             skip=args.offset):

            story = {
                "by": story.doc["by"],
                "id": story.doc["id"],
                "time": story.doc["time"],
                "title": story.doc["title"],
                "url": story.doc["url"],
                "score": story.doc["score"],
                "descendants": story.doc["descendants"],
            }

            stories.append(story)

        return stories


class StoryDetails(Resource):
    @marshal_with(models.story)
    @jwt_required()
    def get(self, story_id):
        config = current_app.config

        server = couchdb.Server(config["HNAC_COUCHDB_SERVER"])
        db = server[config["HNAC_COUCHDB_DATABASE"]]

        doc_id = "hackernews/item/{}".format(story_id)

        doc = db.get(doc_id)

        if not doc:
            abort(
                404,
                error="story doesn't exist",
                story_id=story_id
            )

        del doc["_id"]
        del doc["_rev"]

        return doc
