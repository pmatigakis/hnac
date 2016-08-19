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

        server = couchdb.Server(config["COUCHDB_SERVER"])
        db = server[config["COUCHDB_DATABASE"]]

        stories = []

        for row in db.view("_all_docs", limit=args.limit,
                           include_docs=True, descending=True,
                           skip=args.offset):
            stories.append(row.doc["data"])

        return stories


class StoryDetails(Resource):
    @marshal_with(models.story)
    @jwt_required()
    def get(self, story_id):
        config = current_app.config

        server = couchdb.Server(config["COUCHDB_SERVER"])
        db = server[config["COUCHDB_DATABASE"]]

        doc_id = "hackernews/item/{}".format(story_id)

        doc = db.get(doc_id)

        if not doc:
            abort(
                404,
                error="story doesn't exist",
                story_id=story_id
            )

        return doc["data"]
