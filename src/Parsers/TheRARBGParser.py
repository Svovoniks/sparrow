# from typing import List, Optional
import asyncio
import re
import html
import requests
import urllib.parse
from termcolor import colored
from src.Show import Show

from src.Parsers.NonMagicParserBase import NonMagicParserBase
from src.TorrentUtils import MagnetChecker
from src.utils import HiddenPrints

THE_RARBG_PARSER_NAME = 'TheRARBG'

class TheRARBGParser(NonMagicParserBase):
    def __init__(self) -> None:
        super().__init__()
        self.parser_name = THE_RARBG_PARSER_NAME
        self.search_url = 'https://therarbg.com/get-posts/keywords:{}:category:Movies:category:TV/'
        self.page_url = '?page={}&'
        self.main_url = 'https://therarbg.com'
    
    def get_magnet(self, episode):
        page = self.load_page(self.main_url + episode[1])
        if page is None:
            return None
        
        magnet_pattern = r'''<button onclick="copy\('([^']+)','#copy_magnet'\)"'''
        sc = re.search(magnet_pattern, page.text)
        if sc is None:
            return None
        
        return html.unescape(sc[1])
    
    # def strip_filename(self, filename: str):
    #     return filename.replace(' ', '').replace('.', '').replace('-', '')
    
    # def check_show(self, show: Show, download_folder_contents):
    #     episodes = self.get_all_show_episodes(show.title, show.link)
        
    #     to_download = []
        
    #     download_folder_contents = list(map(self.strip_filename, download_folder_contents))
        
    #     for episode in self.apply_filter(self.process_user_filter(show.filter), episodes):
    #         if self.strip_filename(episode[0]) in download_folder_contents:
    #             return to_download
            
    #         print(f'Missing "{episode[0]}"')
            
    #         magnet = self.get_magnet(episode)
            
    #         if magnet is None:
    #             print(colored(f"Couldn't get magnet link for {episode[0]}", 'red'))
    #             continue
            
    #         to_download.append(self.get_magnet(episode))
        
    #     return to_download
    
    def process_query(self, query):
        return self.search_url.format(urllib.parse.quote(query))
    
    def retrieve_size(self, size_str):
        size_pattern = r'''^(\d*\.*\d*)[\s\S]+?(..)'''
        sc = re.search(size_pattern, size_str)
        if sc is None:
            return f"Unknown size ({size_str})"
        return f'{sc[1]} {sc[2]}'
    
    def get_all_shows_from_page(self, page, episodes, limit, stop_after=None):
        # entry_pattern = r'''<tr class="list-entry [^"]+">[\s\S]+?<a href="([^"]+)"[^>]+>([^<]+)<[\s\S]+?class="sizeCell"[\s\S]+?>([^<]+)<'''
        entry_pattern = r'''<tr class="list-entry[^"]*">[\s\S]+?<a[\s\S]+?href="([^"]+)"[^>]+>([^<]+)<[\s\S]+?class="sizeCell"[\s\S]+?>([^<]+)<'''
        # ^^^ (link_to_the_post, file_name, size) ^^^
        
        found = 0
        
        for i in re.findall(entry_pattern, page.text):
            if stop_after == i[1] and stop_after is not None:
                return 0
            
            if len(episodes) < limit:
                found += 1
                episodes.append((i[1], i[0], self.retrieve_size(i[2])))
            else:
                break
        
        return found
    
    def try_get_next_page(slef, page):
        nav_pattern = r'''<nav>([\s\S]+?)</nav>'''
        sc = re.search(nav_pattern, page.text)
        
        if sc is None:
            return None
        
        next_page_pattern = r'''<li class="page-item active">[\s\S]+?<[\s\S]+?>(\d+)<[\s\S]+?<li class="page-item">[\s\S]+?>(\d+)<'''
        # ^^^ (cur_page_num, next_page_num) ^^^
        
        next_sc = re.search(next_page_pattern, sc[1])
        
        if next_sc is None:
            return None
        
        return next_sc[2]
        
    
    def get_all_show_episodes(self, show: Show, limit, stop_after=None):
        page = self.load_page('https://therarbg.com/post-detail/68d86c/silo-2023-s01-1080p-ds4k-atvp-webrip-ddp5-1-10bit-x265-tovar/')
        
        episodes = []
        
        page = self.load_page(show.link)
        
        if page is None:
            return episodes
        
        found = self.get_all_shows_from_page(page, episodes, limit, stop_after)
        
        while True:
            next_page_num = self.try_get_next_page(page)
            if next_page_num is None:
                break
            
            page = self.load_page(show.link + self.page_url.format(next_page_num))
            
            if page is None:
                break
            
            found = self.get_all_shows_from_page(page, episodes, limit, stop_after)
            
            if found == 0 or len(episodes) >= limit:
                break
        
        return episodes
    


