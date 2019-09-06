import datetime

from switter.client import Switter


def test_twitter():
    """Twitter accound should provide some fixed information"""
    twitter = Switter().profile('twitter')

    assert twitter['id'] == 783_214
    assert twitter['screen_name'] == 'Twitter'
    assert twitter['name'] == 'Twitter'

    assert not twitter['private']

    assert twitter['location'] == "Everywhere"
    assert twitter['website'] == 'https://about.twitter.com/'
    assert twitter['description'] == "What\u2019s happening?!"

    assert twitter['following_count'] > 0
    assert twitter['followers_count'] > 56_600_000
    assert twitter['favorites_count'] > 6200
    assert twitter['tweets_count'] > 11500

    assert twitter['created_at'] == datetime.datetime(
        2007, 2, 20, 14, 35, 54, tzinfo=datetime.timezone.utc
    )


def test_pineapple_search():
    tweets = Switter().search('pineapple')
    assert len(tweets) > 0

    fields = ('text', 'user_screen_name', 'user_name', 'mentions')

    for tweet in tweets:
        assert any('pineapple' in (tweet[field] or '').lower() for field in fields)
