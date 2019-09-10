import datetime
import html
import json
import urllib.parse

from typing import Iterable, List, Optional, Tuple

from requests_html import Element, HTML, HTMLSession  # type: ignore

_CHROME_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'  # noqa: E501

INITIAL_CURSOR = -1


def _extract_tweets(html: HTML) -> List[Element]:
    return html.find('li[data-item-type=tweet]')


def _parse_tweet(tweet: Element) -> dict:
    div = tweet.find('div.tweet', first=True)
    timestamp = tweet.find('a.tweet-timestamp > span._timestamp', first=True)

    created_at = datetime.datetime.fromtimestamp(
        int(timestamp.attrs['data-time-ms']) / 1000, tz=datetime.timezone.utc
    )

    return {
        'id': int(div.attrs['data-tweet-id']),
        'conversation_id': int(div.attrs['data-conversation-id']),
        'created_at': created_at,
        'user_id': int(div.attrs['data-user-id']),
        'user_name': div.attrs['data-name'],
        'user_screen_name': div.attrs['data-screen-name'],
        'text': div.find('p.tweet-text', first=True).text,
        'replies_count': _tweet_stat(div, 'reply'),
        'retweets_count': _tweet_stat(div, 'retweet'),
        'favorites_count': _tweet_stat(div, 'favorite'),
        'mentions': div.attrs.get('data-mentions', '').split(),
    }


def _tweet_stat(tweet: Element, name: str) -> int:
    return int(
        tweet.find(
            f'span.ProfileTweet-action--{name} > span.ProfileTweet-actionCount',
            first=True,
        ).attrs['data-tweet-stat-count']
    )


def _parse_followers_screen_names(document: HTML) -> List[str]:
    cells = document.find(
        'div.profile div.user-list table.user-item tr td.info.screenname'
    )
    return [cell.find('a[name]', first=True).attrs['name'] for cell in cells]


def _parse_followers_cursor(document: HTML) -> Optional[int]:
    next_page_button = document.find('div.w-button-more a', first=True)
    if not next_page_button:
        return None

    next_page_url = next_page_button.attrs['href']
    next_page_qs = urllib.parse.parse_qs(urllib.parse.urlparse(next_page_url).query)

    cursors = next_page_qs['cursor']
    assert len(cursors) == 1
    return int(cursors[0])


class Switter:
    def __init__(self):
        self._session = HTMLSession()
        self._session.headers.update({'User-Agent': _CHROME_USER_AGENT})

        self._enable_legacy_site()

    def _enable_legacy_site(self):
        self._session.cookies.set('m5', 'off')

    def _profile_html(self, screen_name: str) -> HTML:
        url = f'https://twitter.com/{screen_name}'
        response = self._session.get(url)
        response.raise_for_status()
        return response.html

    def _search_json(self, query: str, max_position: Optional[int] = None) -> dict:
        url = 'https://twitter.com/i/search/timeline'
        response = self._session.get(
            url, params={'q': query, 'f': 'tweets', 'max_position': max_position or -1}
        )
        response.raise_for_status()
        return response.json()

    def profile(self, screen_name: str) -> dict:
        document = self._profile_html(screen_name)
        data = json.loads(
            html.unescape(
                document.find(
                    'input.json-data[id=init-data][type=hidden]', first=True
                ).attrs['value']
            )
        )
        user = data['profile_user']
        date_format = r'%a %b %d %H:%M:%S %z %Y'

        return dict(
            id=user['id'],
            name=user['name'],
            screen_name=user['screen_name'],
            location=user['location'],
            website=user['url'],
            description=user['description'],
            created_at=datetime.datetime.strptime(user['created_at'], date_format),
            following_count=user['friends_count'],
            followers_count=user['followers_count'],
            favorites_count=user['favourites_count'],
            tweets_count=user['statuses_count'],
            private=user['protected'],
        )

    def followers(self, screen_name: str) -> Iterable[str]:
        cursor: Optional[int] = INITIAL_CURSOR
        while cursor is not None:
            screen_names, cursor = self.followers_page(screen_name, cursor)
            yield from screen_names

    def followers_page(
        self, screen_name: str, cursor: int = INITIAL_CURSOR
    ) -> Tuple[List[str], Optional[int]]:
        response = self._session.get(
            f'https://mobile.twitter.com/{screen_name}/followers',
            params={'cursor': cursor} if cursor != INITIAL_CURSOR else None,
        )
        response.raise_for_status()

        document = response.html

        screen_names = _parse_followers_screen_names(document)
        next_cursor = _parse_followers_cursor(document)

        return screen_names, next_cursor

    def search(self, query: str, *, limit=20) -> Iterable[dict]:
        assert limit > 0

        count = 0
        position = -1

        while True:
            data = self._search_json(query, max_position=position)
            html = HTML(html=data['items_html'])
            tweets = _extract_tweets(html)

            yield from map(_parse_tweet, tweets[: limit - count])
            count += len(tweets)

            if not data['has_more_items'] or count >= limit:
                break

            position = data['min_position']
