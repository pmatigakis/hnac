from flask_login import LoginManager
from werkzeug.security import check_password_hash

from hnac.models import User
from hnac.web import session


login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    return session.query(User).get(user_id)


def authenticate(username, password):
    user = session.query(User).filter_by(username=username).one_or_none()

    if user and check_password_hash(user.password, password):
        return user

    return None


def identity(payload):
    user_id = payload['identity']

    return session.query(User).get(user_id)
