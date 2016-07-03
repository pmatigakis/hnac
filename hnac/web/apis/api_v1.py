from flask import Blueprint
from flask_restplus import Api

from hnac.web.apis.stories import api as stories_ns

blueprint = Blueprint("api", __name__, url_prefix="/api/v1")

api = Api(blueprint)

api.add_namespace(stories_ns)
