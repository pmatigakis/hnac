from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_user, logout_user, login_required

from hnac.web import session
from hnac.models import Story
from hnac.queries.stories import fetch_stories
from hnac.web.forms import LoginForm
from hnac.models import APIUser


frontend = Blueprint("frontend", __name__)


@frontend.route("/")
@login_required
def index():
    latest_stories = fetch_stories(session, limit=5)

    story_count = session.query(Story).count()

    return render_template("index.html",
                           story_count=story_count,
                           latest_stories=latest_stories)


@frontend.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = APIUser.authenticate(session, username, password)

        if not user:
            return render_template("login.html", form=form)

        login_user(user)

        return redirect(url_for("frontend.index"))

    return render_template("login.html", form=form)


@frontend.route("/logout")
def logout():
    logout_user()

    return redirect(url_for("frontend.login"))
