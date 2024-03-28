
import requests
from termcolor import colored
import re
from src.Show import Show

from src.Parsers.NonMagicParserBase import NonMagicParserBase
from src.utils import ask_for_num, print_colored_list, ask_for_input

TOKYO_TOSHOKAN_PARSER_NAME = 'TokyoToshokan'


class TokyoToshokanParser(NonMagicParserBase):
    def __init__(self) -> None:
        super().__init__()
        self.parser_name = TOKYO_TOSHOKAN_PARSER_NAME
        self.main_url = 'https://www.tokyotosho.info/search.php'
        self.search_url = 'https://www.tokyotosho.info/search.php?terms={0}&type=1&searchName=true&searchComment=false&size_min=&size_max=&username='
    
    def process_query(self, key: str):
        key = key.strip()
        key = re.sub(r'\s+', '+', key)
        return self.search_url.format(key)
    
    def get_magnet(self, episode):
        return episode[1]
    
    def get_all_episodes_from_page(self, page, episodes, limit=None, stop_after=None):
        pattern = r'''<td class="desc-top"><a href="([^"]+)"><span class="sprite_magnet"></span></a> <a rel="nofollow" type="application/x-bittorrent" href="[^"]+">(.+?)</a></td><td[^>]+>.+?</td></tr>.+?\| Size: (.+?) \|'''
        
        found = 0
        for i in re.findall(pattern, page.text):
            if limit != None and limit <= len(episodes):
                break
            
            if stop_after == i[1] and stop_after is not None:
                return 0
            
            found += 1
            episodes.append((i[1].replace('<span class="s"> </span>', ''), i[0], i[2]))
        
        return found
    
    def get_all_show_episodes(self, show: Show, limit, stop_after=None):
        page = self.load_page(show.link)
        
        if page == None:
            return []
        
        addon_page_holder_pattern = r'''<p style="text-align: center">[^<]+</p><p style="text-align: center; font-size: 18pt">[^<](.+)</p>'''
        
        all_episodes = []
        
        addon_pages_str = re.search(addon_page_holder_pattern, page.text)
        self.get_all_episodes_from_page(page, all_episodes, limit, stop_after)
        
        if addon_pages_str != None:
            page_id = 2
            
            while limit == None or len(all_episodes) < limit:
                addon_page = self.load_page(show.link+f'&page={page_id}')
                
                if addon_page == None:
                    break
                
                found = self.get_all_episodes_from_page(addon_page, all_episodes, limit, stop_after)
                
                if found == 0:
                    break
                
                page_id += 1
        
        return all_episodes
    