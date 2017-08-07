import logging

from flask import Blueprint, render_template, redirect, url_for, current_app
from flask_login import login_user, logout_user, login_required, current_user
import couchdb

from hnac.web import session
from hnac.web.forms import LoginForm
from hnac.models import User, Report


logger = logging.getLogger(__name__)


blueprint = Blueprint("frontend", __name__)


@blueprint.route("/")
@login_required
def index():
    config = current_app.config

    server = couchdb.Server(config["COUCHDB_SERVER"])
    db = server[config["COUCHDB_DATABASE"]]

    latest_stories = []

    result = db.view(
        "stories/by_doc_id", limit=5, include_docs=True, descending=True)

    for story in result.rows:
        story = {
            "by": story.doc["data"]["by"],
            "id": story.doc["data"]["id"],
            "time": story.doc["data"]["time"],
            "title": story.doc["data"]["title"],
            "url": story.doc["data"]["url"],
            "score": story.doc["data"]["score"],
            "descendants": story.doc["data"]["descendants"],
        }

        latest_stories.append(story)

    latest_reports = Report.get_latest(session)

    return render_template("index.html",
                           story_count=result.total_rows,
                           latest_stories=latest_stories,
                           latest_reports=latest_reports)


@blueprint.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        logger.info("logging in user %s}", username)

        user = User.authenticate(session, username, password)

        if not user:
            logger.warning("failed to authenticate user %s", username)

            return render_template("login.html", form=form)

        login_user(user)

        return redirect(url_for("frontend.index"))

    return render_template("login.html", form=form)


@blueprint.route("/logout")
@login_required
def logout():
    logger.info("logging out user %s", current_user.username)

    logout_user()

    return redirect(url_for("frontend.login"))
