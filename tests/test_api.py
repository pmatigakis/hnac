from unittest import main
import json

from sqlalchemy.exc import SQLAlchemyError

from hnac.models import Story, Url, HackernewsUser
from hnac.web.database import db

from common import WebTestCaseWithUserAccount
from mock_data import load_stories_1


class StoryEndpointTest(WebTestCaseWithUserAccount):
    def setUp(self):
        super(StoryEndpointTest, self).setUp()

        with self.app.app_context():
            hackernews_user = HackernewsUser.create(
                db.session, "hackernews_user_1")
            url = Url.create(db.session, "http://www.example.com")
            story = Story.create(
                session=db.session,
                user=hackernews_user,
                url=url,
                story_id=1234,
                title="test story",
                score=20,
                time=1528828745,
                descendants=5
            )

            try:
                db.session.commit()
            except SQLAlchemyError:
                db.session.rollback()
                self.fail("failed to create mock data")

            self.story_id = story.id

    def test_fail_to_access_endpoint_without_token(self):
        response = self.client.get("/api/v1/story/1234")

        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data.decode("utf-8"))
        self.assertDictEqual(
            data,
            {
                'message': 'The server could not verify that you are '
                           'authorized to access the URL requested. You '
                           'either supplied the wrong credentials (e.g. a '
                           "bad password), or your browser doesn't understand "
                           "how to supply the credentials required."
            }
        )

    def test_fail_to_access_endpoint_with_invalid_token(self):
        response = self.client.get(
            "/api/v1/story/1234",
            headers={
                "Authorization": "invalid-token"
            }
        )

        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data.decode("utf-8"))
        self.assertDictEqual(
            data,
            {
                'message': 'The server could not verify that you are '
                           'authorized to access the URL requested. You '
                           'either supplied the wrong credentials (e.g. a '
                           "bad password), or your browser doesn't understand "
                           "how to supply the credentials required."
            }
        )

    def test_get_story_data(self):
        response = self.client.get(
            "/api/v1/story/1234",
            headers={
                "Authorization": self.test_token
            }
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode("utf-8"))
        self.assertDictEqual(
            data,
            {
                "by": "hackernews_user_1",
                "descendants": 5,
                "id": 1234,
                "score": 20,
                "time": 1528828745,
                "title": "test story",
                "url": "http://www.example.com"
            }
        )

    def test_fail_get_story_data_of_unknown_story(self):
        response = self.client.get(
            "/api/v1/story/00000",
            headers={
                "Authorization": self.test_token
            }
        )

        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data.decode("utf-8"))
        self.assertIn("message", data)
        message = data["message"]
        self.assertIsInstance(message, str)
        self.assertDictEqual(
            data,
            {
                "error": "story doesn't exist",
                "message": message,
                "story_id": 0
            }
        )


class StoriesEndpointTest(WebTestCaseWithUserAccount):
    def setUp(self):
        super(StoriesEndpointTest, self).setUp()

        with self.app.app_context():
            hackernews_user = HackernewsUser.create(
                db.session, "hackernews_user_1")
            url = Url.create(db.session, "http://www.example.com")
            story_1 = Story.create(
                session=db.session,
                user=hackernews_user,
                url=url,
                story_id=1111,
                title="test story 1",
                score=40,
                time=1528828745,
                descendants=5
            )

            story_2 = Story.create(
                session=db.session,
                user=hackernews_user,
                url=url,
                story_id=2222,
                title="test story 2",
                score=30,
                time=1528828755,
                descendants=10
            )

            story_3 = Story.create(
                session=db.session,
                user=hackernews_user,
                url=url,
                story_id=3333,
                title="test story 3",
                score=20,
                time=1528828750,
                descendants=15
            )

            try:
                db.session.commit()
            except SQLAlchemyError:
                db.session.rollback()
                self.fail("failed to create mock data")

            self.story_1_id = story_1.id
            self.story_2_id = story_2.id
            self.story_3_id = story_3.id

    def test_fail_to_access_endpoint_without_token(self):
        response = self.client.get("/api/v1/stories")

        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data.decode("utf-8"))
        self.assertDictEqual(
            data,
            {
                'message': 'The server could not verify that you are '
                           'authorized to access the URL requested. You '
                           'either supplied the wrong credentials (e.g. a '
                           "bad password), or your browser doesn't understand "
                           "how to supply the credentials required."
            }
        )

    def test_fail_to_access_endpoint_with_invalid_token(self):
        response = self.client.get(
            "/api/v1/stories",
            headers={
                "Authorization": "invalid-token"
            }
        )

        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data.decode("utf-8"))
        self.assertDictEqual(
            data,
            {
                'message': 'The server could not verify that you are '
                           'authorized to access the URL requested. You '
                           'either supplied the wrong credentials (e.g. a '
                           "bad password), or your browser doesn't understand "
                           "how to supply the credentials required."
            }
        )

    def test_get_stories(self):
        response = self.client.get(
            "/api/v1/stories",
            headers={
                "Authorization": self.test_token
            }
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode("utf-8"))
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 3)
        self.assertDictEqual(
            data[0],
            {
                'by': 'hackernews_user_1',
                'descendants': 5,
                'id': 1111,
                'score': 40,
                'time': 1528828745,
                'title': 'test story 1',
                'url': 'http://www.example.com'
            }
        )
        self.assertDictEqual(
            data[1],
            {
                'by': 'hackernews_user_1',
                'descendants': 10,
                'id': 2222,
                'score': 30,
                'time': 1528828755,
                'title': 'test story 2',
                'url': 'http://www.example.com'
            }
        )
        self.assertDictEqual(
            data[2],
            {
                'by': 'hackernews_user_1',
                'descendants': 15,
                'id': 3333,
                'score': 20,
                'time': 1528828750,
                'title': 'test story 3',
                'url': 'http://www.example.com'
            }
        )

    def test_get_stories_sorted_by_time(self):
        response = self.client.get(
            "/api/v1/stories",
            query_string={
                "order_by": "time"
            },
            headers={
                "Authorization": self.test_token
            }
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode("utf-8"))
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 3)
        self.assertDictEqual(
            data[0],
            {
                'by': 'hackernews_user_1',
                'descendants': 5,
                'id': 1111,
                'score': 40,
                'time': 1528828745,
                'title': 'test story 1',
                'url': 'http://www.example.com'
            }
        )
        self.assertDictEqual(
            data[1],
            {
                'by': 'hackernews_user_1',
                'descendants': 15,
                'id': 3333,
                'score': 20,
                'time': 1528828750,
                'title': 'test story 3',
                'url': 'http://www.example.com'
            }
        )
        self.assertDictEqual(
            data[2],
            {
                'by': 'hackernews_user_1',
                'descendants': 10,
                'id': 2222,
                'score': 30,
                'time': 1528828755,
                'title': 'test story 2',
                'url': 'http://www.example.com'
            }
        )

    def test_get_stories_sorted_by_score(self):
        response = self.client.get(
            "/api/v1/stories",
            query_string={
                "order_by": "score"
            },
            headers={
                "Authorization": self.test_token
            }
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode("utf-8"))
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 3)
        self.assertDictEqual(
            data[0],
            {
                'by': 'hackernews_user_1',
                'descendants': 15,
                'id': 3333,
                'score': 20,
                'time': 1528828750,
                'title': 'test story 3',
                'url': 'http://www.example.com'
            }
        )
        self.assertDictEqual(
            data[1],
            {
                'by': 'hackernews_user_1',
                'descendants': 10,
                'id': 2222,
                'score': 30,
                'time': 1528828755,
                'title': 'test story 2',
                'url': 'http://www.example.com'
            }
        )
        self.assertDictEqual(
            data[2],
            {
                'by': 'hackernews_user_1',
                'descendants': 5,
                'id': 1111,
                'score': 40,
                'time': 1528828745,
                'title': 'test story 1',
                'url': 'http://www.example.com'
            }
        )

    def test_get_stories_ordered_descending(self):
        response = self.client.get(
            "/api/v1/stories",
            query_string={
                "desc": True
            },
            headers={
                "Authorization": self.test_token
            }
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode("utf-8"))
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 3)
        self.assertDictEqual(
            data[2],
            {
                'by': 'hackernews_user_1',
                'descendants': 5,
                'id': 1111,
                'score': 40,
                'time': 1528828745,
                'title': 'test story 1',
                'url': 'http://www.example.com'
            }
        )
        self.assertDictEqual(
            data[1],
            {
                'by': 'hackernews_user_1',
                'descendants': 10,
                'id': 2222,
                'score': 30,
                'time': 1528828755,
                'title': 'test story 2',
                'url': 'http://www.example.com'
            }
        )
        self.assertDictEqual(
            data[0],
            {
                'by': 'hackernews_user_1',
                'descendants': 15,
                'id': 3333,
                'score': 20,
                'time': 1528828750,
                'title': 'test story 3',
                'url': 'http://www.example.com'
            }
        )

    def test_get_stories_with_offset_and_limit(self):
        response = self.client.get(
            "/api/v1/stories",
            query_string={
                "offset": 1,
                "limit": 1
            },
            headers={
                "Authorization": self.test_token
            }
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode("utf-8"))
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertDictEqual(
            data[0],
            {
                'by': 'hackernews_user_1',
                'descendants': 10,
                'id': 2222,
                'score': 30,
                'time': 1528828755,
                'title': 'test story 2',
                'url': 'http://www.example.com'
            }
        )

    def test_get_stories_with_limit(self):
        response = self.client.get(
            "/api/v1/stories",
            query_string={
                "limit": 1
            },
            headers={
                "Authorization": self.test_token
            }
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode("utf-8"))
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertDictEqual(
            data[0],
            {
                'by': 'hackernews_user_1',
                'descendants': 5,
                'id': 1111,
                'score': 40,
                'time': 1528828745,
                'title': 'test story 1',
                'url': 'http://www.example.com'
            }
        )

    def test_get_stories_with_offset(self):
        response = self.client.get(
            "/api/v1/stories",
            query_string={
                "offset": 1
            },
            headers={
                "Authorization": self.test_token
            }
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode("utf-8"))
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)
        self.assertDictEqual(
            data[0],
            {
                'by': 'hackernews_user_1',
                'descendants': 10,
                'id': 2222,
                'score': 30,
                'time': 1528828755,
                'title': 'test story 2',
                'url': 'http://www.example.com'
            }
        )
        self.assertDictEqual(
            data[1],
            {
                'by': 'hackernews_user_1',
                'descendants': 15,
                'id': 3333,
                'score': 20,
                'time': 1528828750,
                'title': 'test story 3',
                'url': 'http://www.example.com'
            }
        )


class StorySearchEndpointTest(WebTestCaseWithUserAccount):
    def setUp(self):
        super(StorySearchEndpointTest, self).setUp()

        with self.app.app_context():
            load_stories_1(db.session)

            try:
                db.session.commit()
            except SQLAlchemyError:
                db.session.rollback()
                self.fail("failed to create mock data")

    def test_search_requires_authentication(self):
        response = self.client.get(
            "/api/v1/stories/search",
            query_string={
                "q": "username=user_1+score__gte=5+score__lte=20",
                "offset": 0,
                "limit": 500,
                "order_by": "score",
                "desc": "false"
            }
        )

        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data.decode("utf-8"))
        self.assertDictEqual(
            data,
            {
                'message': 'The server could not verify that you are '
                           'authorized to access the '
                           'URL requested. You either supplied the wrong '
                           'credentials (e.g. a '
                           "bad password), or your browser doesn't understand "
                           "how to supply "
                           'the credentials required.'
            }
        )

    def test_search(self):
        response = self.client.get(
            "/api/v1/stories/search",
            query_string={
                "q": "username=user_1+score__gte=5+score__lte=20",
                "offset": 0,
                "limit": 500,
                "order_by": "score",
                "desc": "false"
            },
            headers={
                "Authorization": self.test_token
            }
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode("utf-8"))
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 3)
        self.assertEqual(
            data,
            [
                {
                    'by': 'user_1',
                    'descendants': 3,
                    'id': 4,
                    'score': 7,
                    'time': 1529613970,
                    'title': 'story 4',
                    'url': 'http://www.example.com/page_4'
                },
                {
                    'by': 'user_1',
                    'descendants': 1,
                    'id': 2,
                    'score': 10,
                    'time': 1529613980,
                    'title': 'story 2',
                    'url': 'http://www.example.com/page_2'
                },
                {
                    'by': 'user_1',
                    'descendants': 0,
                    'id': 1,
                    'score': 15,
                    'time': 1529613984,
                    'title': 'story 1',
                    'url': 'http://www.example.com/page_1'
                }
            ]
        )

    def test_search_with_defaults(self):
        response = self.client.get(
            "/api/v1/stories/search",
            query_string={
                "q": "username=user_1+score__gte=5+score__lte=20"
            },
            headers={
                "Authorization": self.test_token
            }
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode("utf-8"))
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 3)
        self.assertEqual(
            data,
            [
                {
                    'by': 'user_1',
                    'descendants': 0,
                    'id': 1,
                    'score': 15,
                    'time': 1529613984,
                    'title': 'story 1',
                    'url': 'http://www.example.com/page_1'
                },
                {
                    'by': 'user_1',
                    'descendants': 1,
                    'id': 2,
                    'score': 10,
                    'time': 1529613980,
                    'title': 'story 2',
                    'url': 'http://www.example.com/page_2'
                },
                {
                    'by': 'user_1',
                    'descendants': 3,
                    'id': 4,
                    'score': 7,
                    'time': 1529613970,
                    'title': 'story 4',
                    'url': 'http://www.example.com/page_4'
                }
            ]
        )

    def test_search_with_desc_sorting(self):
        response = self.client.get(
            "/api/v1/stories/search",
            query_string={
                "q": "username=user_1+score__gte=5+score__lte=20",
                "offset": 0,
                "limit": 500,
                "order_by": "score",
                "desc": "true"
            },
            headers={
                "Authorization": self.test_token
            }
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode("utf-8"))
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 3)
        self.assertEqual(
            data,
            [
                {
                    'by': 'user_1',
                    'descendants': 0,
                    'id': 1,
                    'score': 15,
                    'time': 1529613984,
                    'title': 'story 1',
                    'url': 'http://www.example.com/page_1'
                },
                {
                    'by': 'user_1',
                    'descendants': 1,
                    'id': 2,
                    'score': 10,
                    'time': 1529613980,
                    'title': 'story 2',
                    'url': 'http://www.example.com/page_2'
                },
                {
                    'by': 'user_1',
                    'descendants': 3,
                    'id': 4,
                    'score': 7,
                    'time': 1529613970,
                    'title': 'story 4',
                    'url': 'http://www.example.com/page_4'
                }
            ]
        )

    def test_search_with_limit_and_offset(self):
        response = self.client.get(
            "/api/v1/stories/search",
            query_string={
                "q": "username=user_1+score__gte=5+score__lte=20",
                "offset": 1,
                "limit": 2,
                "order_by": "score",
                "desc": "false"
            },
            headers={
                "Authorization": self.test_token
            }
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode("utf-8"))
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)
        self.assertEqual(
            data,
            [
                {
                    'by': 'user_1',
                    'descendants': 1,
                    'id': 2,
                    'score': 10,
                    'time': 1529613980,
                    'title': 'story 2',
                    'url': 'http://www.example.com/page_2'
                },
                {
                    'by': 'user_1',
                    'descendants': 0,
                    'id': 1,
                    'score': 15,
                    'time': 1529613984,
                    'title': 'story 1',
                    'url': 'http://www.example.com/page_1'
                }
            ]
        )

    def test_invalid_search_argument(self):
        response = self.client.get(
            "/api/v1/stories/search",
            query_string={
                "q": "username=user_1+score__invalid=5+score__lte=20",
                "offset": 0,
                "limit": 500,
                "order_by": "score",
                "desc": "false"
            },
            headers={
                "Authorization": self.test_token
            }
        )

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data.decode("utf-8"))
        self.assertDictEqual(
            data,
            {
                "error": "failed to parse query item",
                "operation": "score__invalid=5"
            }
        )


class UrlStoriesEndpointTests(WebTestCaseWithUserAccount):
    def setUp(self):
        super(UrlStoriesEndpointTests, self).setUp()

        with self.app.app_context():
            load_stories_1(db.session)

            try:
                db.session.commit()
            except SQLAlchemyError:
                db.session.rollback()
                self.fail("failed to create mock data")

    def test_url_stories_endpoint_requires_authentication(self):
        response = self.client.get(
            "/api/v1/url/stories",
            query_string={
                "url": "http://www.example.com/page_1"
            }
        )

        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data.decode("utf-8"))
        self.assertDictEqual(
            data,
            {
                'message': 'The server could not verify that you are '
                           'authorized to access the '
                           'URL requested. You either supplied the wrong '
                           'credentials (e.g. a '
                           "bad password), or your browser doesn't understand "
                           "how to supply "
                           'the credentials required.'
            }
        )

    def test_get_url_stories(self):
        response = self.client.get(
            "/api/v1/url/stories",
            query_string={
                "url": "http://www.example.com/page_1"
            },
            headers={
                "Authorization": self.test_token
            }
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode("utf-8"))
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(
            data,
            [
                {
                    'by': 'user_1',
                    'descendants': 0,
                    'id': 1,
                    'score': 15,
                    'time': 1529613984,
                    'title': 'story 1',
                    'url': 'http://www.example.com/page_1'
                }
            ]
        )

    def test_fail_to_retrieve_stories_of_unknown_url(self):
        response = self.client.get(
            "/api/v1/url/stories",
            query_string={
                "url": "http://www.example.com/unknown_url"
            },
            headers={
                "Authorization": self.test_token
            }
        )

        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data.decode("utf-8"))
        self.assertDictEqual(
            data,
            {
                'error': "url doesn't exist",
                'message': 'You have requested this URI '
                           '[/api/v1/url/stories] but did you '
                           'mean /api/v1/url/stories or /api/v1/stories or '
                           '/api/v1/stories/search ?',
                'url': 'http://www.example.com/unknown_url'
            }
        )


if __name__ == "__main__":
    main()
