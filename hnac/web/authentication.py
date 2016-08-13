from flask_login import LoginManager

from hnac.models import User
from hnac.web import session


login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    return session.query(User).get(user_id)
