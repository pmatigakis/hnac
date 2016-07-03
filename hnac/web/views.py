from flask import Blueprint, render_template

from hnac.web import session
from hnac.models import Story
from hnac.queries.stories import fetch_stories 

frontend = Blueprint("views", __name__)

@frontend.route("/")
def index():    
    latest_stories = fetch_stories(session, limit=5) 

    story_count = session.query(Story).count()

    return render_template("index.html", story_count=story_count, latest_stories=latest_stories)
