from firebase.firebase import FirebaseApplication


def create_hackernews_firebase_app(
        hackernews_api_url="https://hacker-news.firebaseio.com"):
    """Create a firebase application object for hackernews

    :param str hackernews_api_url: the url of the hackernews firebase api
    :rtype: FirebaseApplication
    :return: the firebase application object
    """
    return FirebaseApplication(hackernews_api_url, None)
