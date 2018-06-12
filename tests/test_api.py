from unittest import main
import json

from sqlalchemy.exc import SQLAlchemyError

from hnac.models import Story, Url, HackernewsUser
from hnac.web.database import db

from common import WebTestCaseWithUserAccount


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
                           'authorized to access the URL requested.  You '
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
                           'authorized to access the URL requested.  You '
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
        self.assertDictEqual(
            data,
            {
                "error": "story doesn't exist",
                "message": "You have requested this URI [/api/v1/story/00000] "
                           "but did you mean /api/v1/story/<int:story_id> or "
                           "/api/v1/stories ?",
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
                           'authorized to access the URL requested.  You '
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
                           'authorized to access the URL requested.  You '
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


if __name__ == "__main__":
    main()
