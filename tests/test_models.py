from unittest import TestCase, main

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import IntegrityError

from hnac.models import Base, User, Domain, Url, Story, APIUser

from mock_data import story_1_data


class UserCreationTests(TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")

        Base.metadata.create_all(self.engine)

        self.Session = scoped_session(sessionmaker(bind=self.engine))

    def tearDown(self):
        self.Session.remove()

        Base.metadata.drop_all(self.engine)

    def test_create_user(self):
        session = self.Session()

        username = "user1"

        user = User.create(session, username)

        session.commit()

        self.assertIsNotNone(user)
        self.assertIsNotNone(user.id)
        self.assertEqual(user.username, username)

    def test_fail_to_add_duplicate_user(self):
        session = self.Session()

        username = "user1"

        User.create(session, username)

        session.commit()

        self.assertEqual(User.count(session), 1)

        User.create(session, username)

        self.assertRaises(IntegrityError, session.commit)


class UserRetrievalTests(TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")

        Base.metadata.create_all(self.engine)

        self.Session = scoped_session(sessionmaker(bind=self.engine))

        session = self.Session()

        self.username_1 = "user1"
        self.username_2 = "user2"

        User.create(session, self.username_1)
        User.create(session, self.username_2)

        session.commit()

        session.close()

    def tearDown(self):
        self.Session.remove()

        Base.metadata.drop_all(self.engine)

    def test_get_by_username(self):
        session = self.Session()

        user = User.get_by_username(session, self.username_1)

        self.assertIsNotNone(user)
        self.assertIsNotNone(user.id)
        self.assertEqual(user.username, self.username_1)

    def test_get_user_that_does_not_exist(self):
        session = self.Session()

        user = User.get_by_username(session, "unknown_user")

        self.assertIsNone(user)


class DomainCreationTests(TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")

        Base.metadata.create_all(self.engine)

        self.Session = scoped_session(sessionmaker(bind=self.engine))

    def tearDown(self):
        self.Session.remove()

        Base.metadata.drop_all(self.engine)

    def test_create_domain(self):
        session = self.Session()

        domain_name = "example.com"

        domain_object = Domain.create(session, domain_name)

        session.commit()

        self.assertIsNotNone(domain_object)
        self.assertIsNotNone(domain_object.id)
        self.assertEqual(domain_object.domain, domain_name)


class DomainQueryTests(TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")

        Base.metadata.create_all(self.engine)

        self.Session = scoped_session(sessionmaker(bind=self.engine))

        self.domain_1 = "example1.com"
        self.domain_2 = "example2.com"

        session = self.Session()

        Domain.create(session, self.domain_1)
        Domain.create(session, self.domain_2)
        session.commit()

        session.close()

    def tearDown(self):
        self.Session.remove()

        Base.metadata.drop_all(self.engine)

    def test_get_by_domain_name(self):
        session = self.Session()

        domain_object = Domain.get_by_domain_name(session, self.domain_1)

        self.assertIsNotNone(domain_object)
        self.assertIsNotNone(domain_object.id)
        self.assertEqual(domain_object.domain, self.domain_1)

    def test_get_unknown_domain(self):
        session = self.Session()

        domain = Domain.get_by_domain_name(session, "unknown_domain.com")

        self.assertIsNone(domain)


class UrlCreationTests(TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")

        Base.metadata.create_all(self.engine)

        self.Session = scoped_session(sessionmaker(bind=self.engine))

    def tearDown(self):
        self.Session.remove()

        Base.metadata.drop_all(self.engine)

    def test_create_url(self):
        session = self.Session()

        url = "example.com/page_1"

        url_object = Url.create(session, url)

        session.commit()

        self.assertIsNotNone(url_object)
        self.assertIsNotNone(url_object.id)
        self.assertEqual(url_object.url, url)


class UrlQueryTests(TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")

        Base.metadata.create_all(self.engine)

        self.Session = scoped_session(sessionmaker(bind=self.engine))

        self.url_1 = "example.com/page_1"
        self.url_2 = "example.com.page_2"

        session = self.Session()

        Url.create(session, self.url_1)
        Url.create(session, self.url_2)
        session.commit()

        session.close()

    def tearDown(self):
        self.Session.remove()

        Base.metadata.drop_all(self.engine)

    def test_get_by_domain_name(self):
        session = self.Session()

        url_object = Url.get_by_url(session, self.url_1)

        self.assertIsNotNone(url_object)
        self.assertIsNotNone(url_object.id)
        self.assertEqual(url_object.url, self.url_1)

    def test_get_unknown_url(self):
        session = self.Session()

        url = Url.get_by_url(session, "www.unknown_url.com")

        self.assertIsNone(url)


class StoryCreationTests(TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")

        Base.metadata.create_all(self.engine)

        self.Session = scoped_session(sessionmaker(bind=self.engine))

    def tearDown(self):
        self.Session.remove()

        Base.metadata.drop_all(self.engine)

    def test_save_story(self):
        session = self.Session()

        story = Story.create_from_dict(session, story_1_data)

        session.commit()

        self.assertIsNotNone(story)
        self.assertIsNotNone(story.id)
        self.assertEqual(story.id, story_1_data["id"])
        self.assertEqual(story.user.username, story_1_data["by"])
        self.assertEqual(story.comment_count, story_1_data["descendants"])
        self.assertEqual(story.score, story_1_data["score"])
        self.assertEqual(story.title, story_1_data["title"])
        self.assertEqual(story.url.url, story_1_data["url"])
        self.assertEqual(story.created_at_timestamp, story_1_data["time"])
        self.assertIsNotNone(story.created_at)
        self.assertIsNotNone(story.added_at)
        self.assertIsNone(story.updated_at)


class StoryQueryTests(TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")

        Base.metadata.create_all(self.engine)

        self.Session = scoped_session(sessionmaker(bind=self.engine))

        session = self.Session()

        Story.create_from_dict(session, story_1_data)

        session.commit()

        session.close()

    def tearDown(self):
        self.Session.remove()

        Base.metadata.drop_all(self.engine)

    def test_get_by_id(self):
        session = self.Session()

        story = Story.get_by_id(session, story_1_data["id"])

        self.assertIsNotNone(story)
        self.assertIsNotNone(story.id)
        self.assertEqual(story.id, story_1_data["id"])
        self.assertEqual(story.user.username, story_1_data["by"])
        self.assertEqual(story.comment_count, story_1_data["descendants"])
        self.assertEqual(story.score, story_1_data["score"])
        self.assertEqual(story.title, story_1_data["title"])
        self.assertEqual(story.url.url, story_1_data["url"])
        self.assertEqual(story.created_at_timestamp, story_1_data["time"])
        self.assertIsNotNone(story.created_at)
        self.assertIsNotNone(story.added_at)
        self.assertIsNone(story.updated_at)

    def test_get_unknown_story(self):
        session = self.Session()

        story = Story.get_by_id(session, 0)

        self.assertIsNone(story)


class StoryUpdateTests(TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")

        Base.metadata.create_all(self.engine)

        self.Session = scoped_session(sessionmaker(bind=self.engine))

        session = self.Session()

        Story.create_from_dict(session, story_1_data)

        session.commit()

        session.close()

    def tearDown(self):
        self.Session.remove()

        Base.metadata.drop_all(self.engine)

    def test_update_from_dict(self):
        session = self.Session()

        updated_story_data = story_1_data.copy()
        updated_story_data["score"] = 100
        updated_story_data["descendants"] = 200

        story = Story.update_from_dict(session, updated_story_data)

        session.commit()

        self.assertIsNotNone(story)
        self.assertIsNotNone(story.id)
        self.assertEqual(story.id, story_1_data["id"])
        self.assertEqual(story.user.username, story_1_data["by"])

        self.assertEqual(story.comment_count,
                         updated_story_data["descendants"])

        self.assertEqual(story.score, updated_story_data["score"])
        self.assertEqual(story.title, story_1_data["title"])
        self.assertEqual(story.url.url, story_1_data["url"])
        self.assertEqual(story.created_at_timestamp, story_1_data["time"])
        self.assertIsNotNone(story.created_at)
        self.assertIsNotNone(story.added_at)
        self.assertIsNotNone(story.updated_at)


class APIUserCreationTests(TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")

        Base.metadata.create_all(self.engine)

        self.Session = scoped_session(sessionmaker(bind=self.engine))

    def tearDown(self):
        self.Session.remove()

    def test_create_api_user(self):
        session = self.Session()

        user = APIUser.create(session, "user1", "password")

        self.assertIsNotNone(user)

        session.commit()

        self.assertIsNotNone(user.id)
        self.assertEqual(user.username, "user1")
        self.assertIsNotNone(user.password)
        self.assertTrue(user.active)
        self.assertIsNotNone(user.registered_at)
        self.assertIsNotNone(user.jti)

        session.close()

class APIUserQueryTests(TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")

        Base.metadata.create_all(self.engine)

        self.Session = scoped_session(sessionmaker(bind=self.engine))

        session = self.Session()

        self.username = "user1"
        self.user = APIUser.create(session, self.username, "password")
        session.commit()

        session.close()

    def tearDown(self):
        self.Session.remove()

    def test_get_user_by_username(self):
        session = self.Session()

        user = APIUser.get_by_username(session, self.username)

        self.assertIsNotNone(user)
        self.assertIsNotNone(user.id)
        self.assertEqual(user.username, self.username)
        self.assertIsNotNone(user.password)
        self.assertTrue(user.active)
        self.assertIsNotNone(user.registered_at)
        self.assertIsNotNone(user.jti)
        
        session.close()

    def test_delete_user(self):
        session = self.Session()

        user = APIUser.delete(session, self.username)
        
        self.assertIsNotNone(user)

        session.commit()

        user = session.query(APIUser)\
                      .filter_by(username=self.username)\
                      .one_or_none() 

        self.assertIsNone(user)

class APIUserPasswordManagementTests(TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")

        Base.metadata.create_all(self.engine)

        self.Session = scoped_session(sessionmaker(bind=self.engine))

        session = self.Session()

        self.username = "user1"
        self.password = "password"
        self.user = APIUser.create(session, self.username, self.password)
        session.commit()

        session.close()

    def tearDown(self):
        self.Session.remove()

    def test_change_user_password(self):
        session = self.Session() 
    
        user = APIUser.get_by_username(session, self.username)

        original_password = user.password
        original_jti = user.jti

        new_password = "new_{}".format(self.password)

        user.change_password(new_password)
        session.commit()

        self.assertIsNotNone(user.password)
        self.assertIsNotNone(user.jti)

        self.assertNotEqual(user.password, original_password)
        self.assertNotEqual(user.jti, original_jti)

        session.close()


class APIUserAuthenticationTests(TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")

        Base.metadata.create_all(self.engine)

        self.Session = scoped_session(sessionmaker(bind=self.engine))

        session = self.Session()

        self.unknown_user = "unknown_user"
        self.username = "user1"
        self.password = "password"
        self.user = APIUser.create(session, self.username, self.password)
        session.commit()

        session.close()

    def tearDown(self):
        self.Session.remove()

    def test_authenticate_user(self):
        session = self.Session() 

        user = APIUser.authenticate(session, self.username, self.password)

        self.assertIsNotNone(user)

    def test_fail_to_authenticate_with_invalid_password(self):
        session = self.Session() 

        password = "invalid_{}".format(self.password)

        user = APIUser.authenticate(session, self.username, password)

        self.assertIsNone(user)

    def test_fail_to_authenticate_unknown_user(self):
        session = self.Session() 

        user = APIUser.authenticate(session, self.unknown_user, self.password)

        self.assertIsNone(user)


if __name__ == '__main__':
    main()
