from os import path, remove
from unittest import TestCase, main

from sqlalchemy import create_engine
from hnac.web.app import create_app
from hnac.web.authentication import load_user
from hnac.models import Base, User
from hnac.web import session


class LoadUserTests(TestCase):
    def setUp(self):
        try:
            remove("hnac.db")
        except:
            pass

        settings_file_path = path.join(path.abspath(path.dirname(__file__)),
                                       "settings.py")

        self.app = create_app("testing", settings_file_path)

        engine = create_engine(self.app.config["HNAC_DB"])
        Base.metadata.create_all(engine)

        self.username = "user1"

        user = User.create(session, self.username, "password")
        session.commit()

        self.user_id = user.id

    def tearDown(self):
        remove("hnac.db")

    def test_load_user(self):
        user = load_user(self.user_id)

        self.assertIsNotNone(user)


if __name__ == "__main__":
    main()
