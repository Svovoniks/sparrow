import asyncio
import re
from typing import Optional
from Configuration import CONFIG_FILE
from Parsers.ParserBase import ParserBase
from Show import Show
from TorrentUtils import MagnetChecker

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
    
    
    def get_magnets(self, show_page):
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
        
        pattern = r'{"res":"1080","torrent":"[^"]+","magnet":"([^"]+)","xdcc":"[^"]+"}]}'
        
        print(api_resp.text)
        
        for i in re.findall(pattern, api_resp.text):
            res.append(i)
            
        return res
        
    
    def check_show(self, show: Show, download_folder_contents: str) -> list[str]:
        """
        returns list of magnet links for new episodes of the show named title
        """
        show_page = self.get_show_page_sublink(show.title)
        
        if show_page == None:
            print(f"""Error: couldn't check for updates for "{show.title}")""")
            print(f"Make sure you put show title correctly into the {CONFIG_FILE} file or try adding it again")
            return []
        
        magnets = self.get_magnets(self.search_url + show_page[1:])
        
        to_download = []
        
        for i in magnets:
            filename = asyncio.run(MagnetChecker(i).get_filename())[:-8]
            
            if filename in download_folder_contents:
                return to_download
            
            to_download.append(i)
            
        return to_download
    
    
    @staticmethod
    def get_all_show_titles(title: str) -> list[str]:
        return list(map(lambda a: a[1], SubsPleaseParser().parse_all_shows()))

