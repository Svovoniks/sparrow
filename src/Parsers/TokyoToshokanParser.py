
import requests
from termcolor import colored
import re

from src.Parsers.ParserBase import ParserBase


# from Show import Show


class TokyoToshokanParser(ParserBase):
    def __init__(self) -> None:
        super().__init__()
        self.main_url = 'https://www.tokyotosho.info/search.php'
        self.search_url = 'https://www.tokyotosho.info/search.php?terms={0}&type=1&searchName=true&searchComment=false&size_min=&size_max=&username='
    
    def process_key(self, key: str):
        key = key.strip()
        key = re.sub(r'\s+', '+', key)
        return key
    
    def check_show(self, show, download_folder_contents):
        return []
    
    def get_all_episodes_from_page(self, page, episodes, limit=None):
        pattern = '''<td class="desc-top"><a href="([^"]+)"><span class="sprite_magnet"></span></a> <a rel="nofollow" type="application/x-bittorrent" href="[^"]+">([^<]+)<span class="s"> </span>([^<]+)</a></td>'''
        
        found = 0
        
        for i in re.findall(pattern, page.text):
            if limit != None and limit >= len(episodes): 
                break
            
            found += 1
            episodes.append((i[1] + i[2], i[0]))
        
        return found
    
    
    def get_all_shows(self, key, limit=100):
        """
        Returns:
            list[list[str]]: list of all shows on the site available on the site
            if the form of [[title1, link_to_the_show_page], [title2, link_to_the_show_page]]
        """
        show_url = self.search_url.format(self.process_key(key))
        page = self.load_page(show_url)
        
        if page == None:
            return []
        
        addon_page_holder_pattern = r'''<p style="text-align: center">[^<]+</p><p style="text-align: center; font-size: 18pt">[^<](.+)</p>'''
        
        all_episodes = []
        
        addon_pages_str = re.search(addon_page_holder_pattern, page.text)
        self.get_all_episodes_from_page(page, all_episodes, limit)
        
        if addon_pages_str != None:
            page_id = 2
            
            while limit == None or len(all_episodes) < limit:
                addon_page = self.load_page(show_url+f'&page={page_id}')
                
                if addon_page == None:
                    break
                
                found = self.get_all_episodes_from_page(addon_page, all_episodes, limit)
                
                if found == 0:
                    break
                
                page_id += 1
        
        return all_episodes
    
    def get_show_filter(self, title, link):
        return ''

