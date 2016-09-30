from hnac.models import User


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
