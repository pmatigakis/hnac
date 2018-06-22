from hnac.models import User, Story, Url, HackernewsUser

story_1_data = {
    "by": "eloy",
    "descendants": 1,
    "id": 11976079,
    "score": 2,
    "time": 1466856540,
    "title": "Evil maid goes after Truecrypt (2009)",
    "type": "story",
    "url": "http://theinvisiblethings.blogspot.com/2009/10/evil-maid"
           "-goes-after-truecrypt.html"
}

story_2_data = {
    "title": "Starting Your Big Data Journey with CDH, Docker and Pentaho BA",
    "url": "http://www.lewisgavin.co.uk/CDH-Docker/",
    "descendants": 0,
    "by": "gavlaaaaaaaa",
    "score": 1,
    "time": 1471369583,
    "type": "story",
    "id": 12299134
}


def load_mock_data(session):
    user = User.create(session, "user1", "user1password")

    session.add(user)


def load_stories_1(session):
    user_1 = HackernewsUser.create(session, "user_1")
    user_2 = HackernewsUser.create(session, "user_2")
    url_1 = Url.create(session, "http://www.example.com/page_1")
    url_2 = Url.create(session, "http://www.example.com/page_2")
    url_3 = Url.create(session, "http://www.example.com/page_3")
    url_4 = Url.create(session, "http://www.example.com/page_4")
    url_5 = Url.create(session, "http://www.example.com/page_5")
    story_1 = Story.create(
        session=session,
        user=user_1,
        url=url_1,
        story_id=1,
        title="story 1",
        score=15,
        time=1529613984,
        descendants=0
    )
    story_1.id = 1

    story_2 = Story.create(
        session=session,
        user=user_1,
        url=url_2,
        story_id=2,
        title="story 2",
        score=10,
        time=1529613980,
        descendants=1
    )
    story_2.id = 2

    story_3 = Story.create(
        session=session,
        user=user_2,
        url=url_3,
        story_id=3,
        title="story 3",
        score=18,
        time=1529613990,
        descendants=2
    )
    story_3.id = 3

    story_4 = Story.create(
        session=session,
        user=user_1,
        url=url_4,
        story_id=4,
        title="story 4",
        score=7,
        time=1529613970,
        descendants=3
    )
    story_4.id = 4

    story_5 = Story.create(
        session=session,
        user=user_1,
        url=url_5,
        story_id=5,
        title="story 5",
        score=2,
        time=1529613999,
        descendants=4
    )
    story_5.id = 5
