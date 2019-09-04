import datetime

from switter.client import Switter


def test_twitter():
    """Twitter accound should provide some fixed information"""
    twitter = Switter().profile('twitter')

    assert twitter['id'] == 783_214
    assert twitter['screen_name'] == 'Twitter'
    assert twitter['name'] == 'Twitter'

    assert not twitter['private']

    assert twitter['following_count'] > 30
    assert twitter['followers_count'] > 56_600_000
    assert twitter['favorites_count'] > 6200
    assert twitter['tweets_count'] > 11500

    assert twitter['created_at'] == datetime.datetime(
        2007, 2, 20, 14, 35, 54, tzinfo=datetime.timezone.utc
    )
