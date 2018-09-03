from flask import Blueprint
from flask_restful import Api

from hnac.web.apis import stories
from hnac.web.apis import urls

blueprint = Blueprint("api", __name__)

api = Api(blueprint)

api.add_resource(stories.Stories, "/stories")
api.add_resource(stories.StoryDetails, "/story/<int:story_id>")
api.add_resource(stories.StorySearch, "/stories/search")
api.add_resource(urls.UrlStories, "/url/stories")
