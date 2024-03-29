import datetime

from unittest import mock

import responses

from switter.client import INITIAL_CURSOR


def test_twitter_profile(client):
    """Twitter accound should provide some fixed information"""
    twitter = client.profile('twitter')

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


def test_pineapple_search(client):
    keyword = 'pineapple'
    tweets = list(client.search(keyword))
    assert len(tweets) > 0

    fields = ('text', 'user_screen_name', 'user_name')

    for tweet in tweets:
        assert any(keyword in (tweet[field] or '').lower() for field in fields) or any(
            keyword for mention in tweet['mentions']
        )


def test_search_len(client):
    # default limit should be 20
    assert len(list(client.search('twitter'))) == 20

    # we should be able to go further
    assert len(list(client.search('twitter', limit=50))) == 50


@mock.patch('switter.client.HTML', new=mock.Mock)
@mock.patch('switter.client._parse_tweet', new=mock.Mock)
@mock.patch('switter.client._extract_tweets')
@mock.patch('switter.client.Switter._search_json')
def test_search(search_json, extract_tweets, client):
    search_json.return_value = {
        'items_html': mock.Mock(),
        'has_more_items': True,
        'min_position': mock.Mock,
    }

    extract_tweets.return_value = list(range(20))

    for limit in (5, 10, 20, 50):
        result = list(client.search('foo', limit=limit))
        assert len(result) == limit

    # only one page available
    search_json.return_value = {'items_html': mock.Mock(), 'has_more_items': False}

    for limit in (5, 10, 20, 50):
        result = list(client.search('foo', limit=limit))
        assert len(result) == min(limit, 20)


@responses.activate
def test_followers_page(
    client, followers_empty_html, followers_full_html, followers_last_html
):
    base = 'https://mobile.twitter.com'

    for url, body in (
        (f'{base}/full/followers?cursor=123456789', followers_empty_html),
        (f'{base}/full/followers', followers_full_html),
        (f'{base}/last/followers', followers_last_html),
    ):
        responses.add(responses.GET, url, body=body, content_type='text/html')

    followers, cursor = client.followers_page('full')
    assert followers == ['alice', 'bob', 'carol']
    assert cursor == 123_456_789

    followers, cursor = client.followers_page('full', cursor=cursor)
    assert followers == []
    assert cursor is None

    followers, cursor = client.followers_page('last', cursor=cursor)
    assert followers == ['david']
    assert cursor is None


@mock.patch('switter.client.Switter.followers_page')
def test_followers(followers_page, client):
    followers_page.return_value = (), None
    assert list(client.followers('foo')) == []

    followers_page.assert_called_once_with('foo', INITIAL_CURSOR)
    followers_page.reset_mock()

    followers_page.side_effect = (
        (('a', 'b', 'c'), 1),
        (('d', 'e', 'f'), 2),
        (('g', 'h'), None),
        (('i', 'j', 'k'), 3),  # should not be reached
    )
    assert list(client.followers('foo')) == list('abcdefgh')
    followers_page.assert_has_calls(
        (mock.call('foo', INITIAL_CURSOR), mock.call('foo', 1), mock.call('foo', 2))
    )
