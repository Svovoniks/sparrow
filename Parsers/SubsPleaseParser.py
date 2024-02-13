import asyncio
import re
from Parsers.ParserBase import ParserInterface
from main import MagnetChecker


class SubsPleaseParser(ParserInterface):
    def __init__(self, download_folder_contents) -> None:
        super().__init__(download_folder_contents)
        self.parser_name = 'SubsPlease'
        self.search_url = 'https://subsplease.org/shows/'
        self.api_url = 'https://subsplease.org/api/?f=show&tz=Europe/Moscow&sid={}'

    def get_title_page_sublink(self, exact_title):
        pattern = r"""<div class="all-shows-link"><a href="([^"]+)" title="([^"]+)">([^<]+)</a>"""
        
        resp = self.load_page(self.search_url)
        
        if resp == None:
            return None
        
        for i in re.findall(pattern, resp.text):
            print(i)
            if i[1] == exact_title:
                return i[0]
        
        return None
    
    def get_sid(self, title_page):
        page = self.load_page(title_page)
        
        if page == None:
            return None
        
        pattern = r'sid="(\d+)"'
        
        found = re.search(pattern, page.text)
        
        if found == None:
            return None
        
        return found[1]
    
    
    def get_magnets(self, title_page):
        sid = self.get_sid(title_page)
        
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
        
    
    def check_title(self, title):
        title_page = self.get_title_page_sublink(title)
        
        if title_page == None:
            return False
        
        magnets = self.get_magnets(self.search_url + title_page[1:])
        
        to_download = []
        
        for i in magnets:
            filename = asyncio.run(MagnetChecker(i).get_filename())[:-8]
            
            if filename in self.download_folder_contents:
                return to_download
            
            to_download.append(i)
            
        return to_download

