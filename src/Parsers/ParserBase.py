# from typing import List, Optional
import requests
from termcolor import colored

# from Show import Show


class ParserBase:
    def __init__(self) -> None:
        pass
    
    def check_show(self, show, download_folder_contents: set[str]) -> list[str]:
        return []
    
    def get_all_shows(self) -> list[list[str]]:
        """
        Returns:
            list[list[str]]: list of all shows on the site available on the site
            if the form of [[title1, link_to_the_show_page], [title2, link_to_the_show_page]]
        """
        return []
    
    def get_show_filter(self, title, link):
        return ''
    
    def load_page(self, url):
        """loads a url
        Args:
            url (str): _description_

        Returns:
            None: if page could't be loaded
            Responce: otherwise
        """
        
        try:
            resp = requests.get(url)
            
            if resp.status_code != 200:
                print(colored(f"Couldn't load {url}", 'red'))
                return None
        except:
            print(colored(f"Couldn't load {url}", 'red'))
            return None
        return resp

