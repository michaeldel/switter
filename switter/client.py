import datetime
import html
import json
import requests

from bs4 import BeautifulSoup


class Switter:
    def _profile_html(self, screen_name: str) -> str:
        url = f'https://twitter.com/{screen_name}'
        response = requests.get(url)
        response.raise_for_status()
        return response.text

    def profile(self, screen_name: str) -> dict:
        profile_html = self._profile_html(screen_name)
        document = BeautifulSoup(profile_html, 'lxml')
        data = json.loads(
            html.unescape(
                document.find(
                    'input',
                    attrs={'id': 'init-data', 'class': 'json-data', 'type': 'hidden'},
                ).attrs['value']
            )
        )
        user = data['profile_user']
        date_format = r'%a %b %d %H:%M:%S %z %Y'

        return dict(
            id=user['id'],
            name=user['name'],
            screen_name=user['screen_name'],
            created_at=datetime.datetime.strptime(user['created_at'], date_format),
            following_count=user['friends_count'],
            followers_count=user['followers_count'],
            favorites_count=user['favourites_count'],
            tweets_count=user['statuses_count'],
            private=user['protected'],
        )
