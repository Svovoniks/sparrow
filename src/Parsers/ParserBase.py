# from typing import List, Optional
import requests
from termcolor import colored

from src.Show import Show



class ParserBase:
    def __init__(self) -> None:
        pass

    def apply_filter(self, _filter, episodes):
        raise NotImplementedError

    def process_user_filter(self, _filter):
        return _filter

    def get_magnet(self, episode):
        '''
        returns magnet link for a given episode (the "get_all_show_episodes" return tuple)
        '''
        raise NotImplementedError

    def get_all_show_episodes(self, show, limitб, stop_after=None):
        '''
        return a list of all episodes that satisfy user query as a list[(episode_title, ... ), ...]
        the length of the list shouldn't exceed limit unless it's set to None
        '''
        raise NotImplementedError

    def check_show(self, show: Show, to_download):
        episodes = self.get_all_show_episodes(show, 200, show.last_episode)

        new_last = None

        for episode in self.apply_filter(self.process_user_filter(show.filter), episodes):
            if new_last is None:
                new_last = episode[0]

            if show.last_episode is not None and show.last_episode == episode[0]:
                return new_last

            print(f'Missing "{episode[0]}"')
            to_download.append(self.get_magnet(episode))

        return new_last

    def get_all_shows(self, key):
        """
        Returns:
            list[list[str]]: list of all shows on the site available on the site
            if the form of [[title1, link_to_the_show_page], [title2, link_to_the_show_page]]
        """
        return []

    def get_show_filter(self, title, link):
        return ''

    def load_page(self, url, cookies=[]):
        """loads a url
        Args:
            url (str): _description_

        Returns:
            None: if page could't be loaded
            Response: otherwise
        """
        try:
            resp = requests.get(url, cookies=cookies)

            if resp.status_code != 200:
                print(colored(f"Couldn't load {url}", 'red'))
                return None
        except:
            print(colored(f"Couldn't load {url}", 'red'))
            return None
        return resp

