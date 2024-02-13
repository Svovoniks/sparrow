from typing import List, Optional
import requests

from Show import Show


class ParserBase:
    def __init__(self, parser_name) -> None:
        self.parser_name = parser_name
    
    
    # checks title for updates and returns magnet links
    # for new episodes to be downloaded
    def check_show(self, show: Show, download_folder_contents: str) -> list[str]:
        return []
    
    @staticmethod
    def get_all_show_titles(title: str) -> list[str]:
        return []
    
    def load_page(self, url):
        resp = requests.get(url)
        
        if resp.status_code != 200:
            print(f"Couldn't load {self.parser_name}")
            return None
        
        return resp

