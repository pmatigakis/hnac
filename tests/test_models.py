from unittest import TestCase, main

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from hnac.models import Base, User


class UserCreationTests(TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")

        Base.metadata.create_all(self.engine)

        self.Session = scoped_session(sessionmaker(bind=self.engine))

    def tearDown(self):
        self.Session.remove()

    def test_create_api_user(self):
        session = self.Session()

        user = User.create(session, "user1", "password")

        self.assertIsNotNone(user)

        session.commit()

        self.assertIsNotNone(user.id)
        self.assertEqual(user.username, "user1")
        self.assertIsNotNone(user.password)
        self.assertTrue(user.active)
        self.assertIsNotNone(user.registered_at)

        session.close()


class UserQueryTests(TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")

        Base.metadata.create_all(self.engine)

        self.Session = scoped_session(sessionmaker(bind=self.engine))

        session = self.Session()

        self.username = "user1"
        self.user = User.create(session, self.username, "password")
        session.commit()

        session.close()

    def tearDown(self):
        self.Session.remove()

    def test_get_user_by_username(self):
        session = self.Session()

        user = User.get_by_username(session, self.username)

        self.assertIsNotNone(user)
        self.assertIsNotNone(user.id)
        self.assertEqual(user.username, self.username)
        self.assertIsNotNone(user.password)
        self.assertTrue(user.active)
        self.assertIsNotNone(user.registered_at)

        session.close()

    def test_delete_user(self):
        session = self.Session()

        user = User.delete(session, self.username)

        self.assertIsNotNone(user)

        session.commit()

        user = session.query(User)\
                      .filter_by(username=self.username)\
                      .one_or_none()

        self.assertIsNone(user)


class UserPasswordManagementTests(TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")

        Base.metadata.create_all(self.engine)

        self.Session = scoped_session(sessionmaker(bind=self.engine))

        session = self.Session()

        self.username = "user1"
        self.password = "password"
        self.user = User.create(session, self.username, self.password)
        session.commit()

        session.close()

    def tearDown(self):
        self.Session.remove()

    def test_change_user_password(self):
        session = self.Session()

        user = User.get_by_username(session, self.username)

        original_password = user.password

        new_password = "new_{}".format(self.password)

        user.change_password(new_password)
        session.commit()

        self.assertIsNotNone(user.password)

        self.assertNotEqual(user.password, original_password)

        session.close()


class UserAuthenticationTests(TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")

        Base.metadata.create_all(self.engine)

        self.Session = scoped_session(sessionmaker(bind=self.engine))

        session = self.Session()

        self.unknown_user = "unknown_user"
        self.username = "user1"
        self.password = "password"
        self.user = User.create(session, self.username, self.password)
        session.commit()

        session.close()

    def tearDown(self):
        self.Session.remove()

    def test_authenticate_user(self):
        session = self.Session()

        user = User.authenticate(session, self.username, self.password)

        self.assertIsNotNone(user)

    def test_fail_to_authenticate_with_invalid_password(self):
        session = self.Session()

        password = "invalid_{}".format(self.password)

        user = User.authenticate(session, self.username, password)

        self.assertIsNone(user)

    def test_fail_to_authenticate_unknown_user(self):
        session = self.Session()

        user = User.authenticate(session, self.unknown_user, self.password)

        self.assertIsNone(user)


if __name__ == '__main__':
    main()
