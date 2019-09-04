import requests

from bs4 import BeautifulSoup


def _profile_nav_stat(navigation: BeautifulSoup, name: str) -> int:
    assert navigation.name == 'div'
    assert 'ProfileNav' in navigation.attrs['class']
    assert navigation.attrs['role'] == 'navigation'

    return int(
        navigation.find('a', attrs={'class': 'ProfileNav-stat', 'data-nav': name})
        .find('span', attrs={'class': 'ProfileNav-value'})
        .attrs['data-count']
    )


def _profile_navigation(document: BeautifulSoup) -> BeautifulSoup:
    return document.find('div', attrs={'class': 'ProfileNav', 'role': 'navigation'})


def _profile_user_actions(document: BeautifulSoup) -> BeautifulSoup:
    return document.select_one('div.user-actions.btn-group.not-following')


def _is_profile_private(user_actions: BeautifulSoup) -> bool:
    protected = user_actions.attrs['data-protected']
    if protected == 'false':
        return False
    if protected == 'true':
        return True
    raise ValueError(f"Unexpected data-protected value: {protected}")


class Switter:
    def _profile_html(self, screen_name: str) -> str:
        url = f'https://twitter.com/{screen_name}'
        response = requests.get(url)
        response.raise_for_status()
        return response.text

    def profile(self, screen_name: str) -> dict:
        html = self._profile_html(screen_name)
        document = BeautifulSoup(html, 'lxml')

        user_actions = _profile_user_actions(document)
        navigation = _profile_navigation(document)

        return dict(
            id=int(user_actions.attrs['data-user-id']),
            name=user_actions.attrs['data-name'],
            screen_name=user_actions.attrs['data-screen-name'],
            private=_is_profile_private(user_actions),
            tweets=_profile_nav_stat(navigation, 'tweets'),
            following=_profile_nav_stat(navigation, 'following'),
            followers=_profile_nav_stat(navigation, 'followers'),
            favorites=_profile_nav_stat(navigation, 'favorites'),
        )
