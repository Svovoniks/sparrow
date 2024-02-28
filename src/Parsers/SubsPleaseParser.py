import asyncio
import re

from termcolor import colored
from src.Parsers.ParserBase import ParserBase
from src.Show import Show
from src.TorrentUtils import MagnetChecker
from src.utils import ask_for_input

SUBS_PLEASE_PARSER_NAME = 'SubsPlease'


class SubsPleaseParser(ParserBase):
    def __init__(self) -> None:
        super().__init__()
        self.search_url = 'https://subsplease.org/shows/'
        self.api_url = 'https://subsplease.org/api/?f=show&tz=Europe/Moscow&sid={}'
        
        
    def parse_all_shows(self) -> list[list[str]]:
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

    def get_show_page_sublink(self, exact_title: str):
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
    
    
    def get_magnets(self, show_page, show_filter):
        """
        returns magnet links from show_page
        """
        sid = self.get_sid(show_page)
        
        res = []
        
        if sid == None:
            return res
        
        api_resp = self.load_page(self.api_url.format(sid))
        
        if api_resp == None:
            return res
        
        pattern = r'{"res":"' + show_filter + '","torrent":"[^"]+","magnet":"([^"]+)","xdcc":"[^"]+"}'
        
        for i in re.findall(pattern, api_resp.text):
            res.append(i)
            
        return res
        
    
    def check_show(self, show: Show, download_folder_contents: set[str]) -> list[str]:
        """
        returns list of magnet links for new episodes of the show named title
        """
        magnets = self.get_magnets(show.link, show.filter)
        
        to_download = []
        
        for i in magnets:
            filename = asyncio.run(MagnetChecker(i).get_filename())[:-8]
            
            if filename in download_folder_contents:
                return to_download
            print(f'Missing "{filename}"')
            to_download.append(i)
            
        return to_download
    
    
    def get_all_shows(self) -> list[list[str]]:
        all_shows = SubsPleaseParser().parse_all_shows()
        if all_shows == None:
            return []
        return list(map(lambda a: [a[1], self.search_url + a[0]], all_shows))

