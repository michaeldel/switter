import datetime

from unittest import mock

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
    tweets = list(Switter().search('pineapple'))
    assert len(tweets) > 0

    fields = ('text', 'user_screen_name', 'user_name', 'mentions')

    for tweet in tweets:
        assert any('pineapple' in (tweet[field] or '').lower() for field in fields)


def test_search_len():
    client = Switter()
    # default limit should be 20
    assert len(list(client.search('twitter'))) == 20

    # we should be able to go further
    assert len(list(client.search('twitter', limit=50))) == 50


@mock.patch('switter.client._parse_tweet', new=mock.Mock)
@mock.patch('switter.client.Switter._search_json')
@mock.patch('switter.client._extract_tweets_html')
def test_search(extract_tweets, search_json):
    search_json.return_value = {
        'items_html': mock.Mock(),
        'has_more_items': True,
        'min_position': mock.Mock,
    }

    extract_tweets.return_value = list(range(20))
    client = Switter()

    for limit in (5, 10, 20, 50):
        result = list(client.search('foo', limit=limit))
        assert len(result) == limit

    # only one page available
    search_json.return_value = {'items_html': mock.Mock(), 'has_more_items': False}

    for limit in (5, 10, 20, 50):
        result = list(client.search('foo', limit=limit))
        assert len(result) == min(limit, 20)
