from flask_login import LoginManager
from werkzeug.security import check_password_hash
from flask_jwt import _default_jwt_payload_handler

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
    user_id = payload["identity"]
    jti = payload["jti"]

    return User.authenticate_using_jwt(session, user_id, jti)


def payload_handler(identity):
    payload = _default_jwt_payload_handler(identity)

    payload["jti"] = identity.jti

    return payload
