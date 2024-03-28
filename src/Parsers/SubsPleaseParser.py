import asyncio
import re
import json

from termcolor import colored
from src.Parsers.ParserBase import ParserBase
from src.Show import Show
from src.TorrentUtils import MagnetChecker
from src.utils import HiddenPrints, ask_for_input

SUBS_PLEASE_PARSER_NAME = 'SubsPlease'


class SubsPleaseParser(ParserBase):
    def __init__(self) -> None:
        super().__init__()
        self.search_url = 'https://subsplease.org/shows/'
        self.api_url = 'https://subsplease.org/api/?f=show&tz=Europe/Moscow&sid={}'
        
    
    def get_magnet(self, episode):
        return episode[1]
        
    def parse_all_shows(self):
        """
        returns list of ["show_sublink", "show_title"] for all shows on the site
        """
        pattern = r"""<div class="all-shows-link"><a href="([^"]+)" title="([^"]+)">[^<]+</a>"""
        
        resp = self.load_page(self.search_url)
        
        if resp == None:
            return None
        
        return [i for i in re.findall(pattern, resp.text)]
    
    def get_show_filter(self, title, link):
        print(f'Choose quality for "{title}" [1080/720/480]')
        acceptable = ['1080', '720', '480']
        
        choice = ask_for_input('ask again')
        
        while choice not in acceptable:
            if choice == 'exit':
                exit(0)
            
            print(colored('Invalid input. Please select one of the given options', 'red'))
            print(colored('ProTip: If this conversation starts to feel threatening just type "exit" ', 'cyan'))
            
            choice = ask_for_input('ask again')
        
        print(colored(f'You selected {choice}', 'green'))
        
        return choice

    def get_show_page_sublink(self, exact_title):
        """
        retruns string that needs to be added to search url to get the show page
        """
        for i in self.parse_all_shows():
            if i[1] == exact_title:
                return i[0]
        
        return None
    
    def get_sid(self, show_page):
        """
        returns sid for the show from show_page
        """
        page = self.load_page(show_page)
        
        if page == None:
            return None
        
        pattern = r'sid="(\d+)"'
        
        found = re.search(pattern, page.text)
        
        if found == None:
            return None
        
        return found[1]
    
    def apply_filter(self, _filter, episodes):
        return list(filter(lambda a: a[2] == _filter, episodes))
    
    def get_all_show_episodes(self, show: Show, limit, stop_after=None):
        sid = self.get_sid(show.link)
        
        res = []
        
        if sid == None:
            return res
        
        api_resp = self.load_page(self.api_url.format(sid))
        
        if api_resp == None:
            return res
        
        js = json.loads(api_resp.text)
        
        for i in js['episode'].keys():
            for j in js['episode'][i]['downloads']:
                res.append((i, j['magnet'], j['res']))
            
        return res
    
    
    def get_all_shows(self, key):
        all_shows = SubsPleaseParser().parse_all_shows()
        if all_shows == None:
            return []
        return list(map(lambda a: [a[1], self.search_url + a[0]], all_shows))

