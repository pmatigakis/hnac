import logging

from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user

from hnac.web import session
from hnac.web.forms import LoginForm
from hnac.models import User, Report, Story


logger = logging.getLogger(__name__)


blueprint = Blueprint("frontend", __name__)


@blueprint.route("/")
@login_required
def index():
    latest_stories = []

    for story in Story.get_latest(session, 10):
        story = {
            "by": story.hackernews_user.username,
            "id": story.story_id,
            "time": story.time,
            "title": story.title,
            "url": story.url.url,
            "score": story.score,
            "descendants": story.descendants
        }

        latest_stories.append(story)

    latest_reports = Report.get_latest(session)

    return render_template("index.html",
                           story_count=Story.count(session),
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
