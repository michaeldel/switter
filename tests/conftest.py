import pytest

from switter.client import Switter


@pytest.fixture
def client():
    return Switter()


@pytest.fixture
def followers_full_html(shared_datadir):
    return (shared_datadir / 'followers_full.html').read_text()


@pytest.fixture
def followers_empty_html(shared_datadir):
    return (shared_datadir / 'followers_empty.html').read_text()


@pytest.fixture
def followers_last_html(shared_datadir):
    return (shared_datadir / 'followers_last.html').read_text()
