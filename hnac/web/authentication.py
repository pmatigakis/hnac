from flask_login import LoginManager
from flask_uauth.uauth import UAuth

from hnac.models import User, Token
from hnac.web.database import db


uauth = UAuth()
login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)


def authentication_callback(authorization_value):
    return Token.get_by_value(db.session, authorization_value)
