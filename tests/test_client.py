from switter.client import Switter


def test_twitter():
    """Twitter accound should provide some fixed information"""
    twitter = Switter().profile('twitter')

    assert twitter['id'] == 783_214
    assert twitter['screen_name'] == 'Twitter'
    assert twitter['name'] == 'Twitter'

    assert not twitter['private']

    assert twitter['following'] > 30
    assert twitter['followers'] > 56_600_000
    assert twitter['favorites'] > 6200
    assert twitter['tweets'] > 11500
