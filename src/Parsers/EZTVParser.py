import asyncio

from termcolor import colored
from src.Parsers.ParserBase import ParserBase
import re
from functools import reduce
from src.Show import Show

from src.utils import ask_for_num, print_colored_list, ask_for_input

EZTV_PARSER_NAME = 'EZTV'

class EZTVParser(ParserBase):
    def __init__(self) -> None:
        super().__init__()
        self.main_url = 'https://eztvx.to/'
        self.all_shows_url = 'https://eztvx.to/showlist/'
        self.episode_num_pattern = r'(S\d\dE\d\d)'
        
    # def check_show(self, show: Show, download_folder_contents):
    #     episodes = self.get_all_show_episodes(show.link)
        
    #     to_download = []
        
    #     for idx in self.apply_filter(episodes, show.filter):
    #         page = self.load_page(self.main_url + episodes[idx][0])
            
    #         magnet = self.get_magnet(page)
    #         filename = self.get_torrent_filename(page)
            
    #         if filename == None: continue
            
    #         if filename in download_folder_contents:
    #             return to_download
            
    #         print(f'Missing "{filename}"')
    #         to_download.append(magnet)
        
    #     return to_download
    
    def get_torrent_filename(self, page):
        pattern = r'''<a href="([^"]+)" title="Download Torrent" rel="nofollow">'''
        
        tor_link = re.search(pattern, page.text)[1]
        
        return tor_link[tor_link.rfind('/')+1:-8]
    
    def get_magnet(self, episode):
        pattern = r'''<a href="([^"]+)" title="Magnet Link">'''
        
        page = self.load_page(self.main_url + episode[1])
        
        return re.search(pattern, page.text)[1]
        
    
    def get_all_shows(self, key):
        """
        Returns:
            list[list[str]]: list of all shows on the site available on the site
            if the form of [[title1, link_to_the_show_page], [title2, link_to_the_show_page]]
        """
        page = self.load_page(self.all_shows_url)
        pattern = r'''<td class="forum_thread_post"><a href="([^"]+)" class="thread_link">([^"]+)</a></td>'''
        
        if page == None:
            return []
        
        return [(i[1], self.main_url + i[0]) for i in re.findall(pattern, page.text)]
    
    
    def get_all_show_episodes(self, show: Show):
        page = self.load_page(show.link)
        
        if page is None:
            return []
        
        pattern = r'''<a href="([^"]+)" title="[^"]+" alt="([^"]+)\(([^"]+)\)" class="epinfo">[^"]+</a>\n</td>'''
        all_episodes = []
        
        for i in re.findall(pattern, page.text):
            all_episodes.append((i[1], i[0], i[2]))
        
        return all_episodes
        
    def get_filter(self, ep_title):
        return re.sub(self.episode_num_pattern, '<<episode_number>>', ep_title)
    
    def apply_filter(self, _filter, episodes):
        return list(filter(lambda a: self.get_filter(a[0]) == _filter, episodes))
    
    
    def ask_for_filter(self, episodes, title):
        if len(episodes) == 0:
            print(colored(f'''"{title}" doesn't have any episodes at the moment''', 'red'))
            print(colored(f"So i can't create a show filter right now, plese try again later", 'red'))
            print(colored(f"Exiting", 'red'))
            exit(1)
        
        print(f'Here is a list of all episode for {title}')
        print_colored_list(episodes, mapper=lambda a: (a[0], a[2]))
        
        ep_num = ask_for_num('\nPlease eneter the number of the episode from which you want me to create episode filter\n', len(episodes))
        
        ep_filter = self.get_filter(episodes[ep_num-1][0])
        
        print('\nAfter applying the filter only these episodes remain:')
        
        print_colored_list(self.apply_filter(ep_filter, episodes), mapper=lambda a: (a[0], a[2]))
        
        print('Is that correct?')
        print('Enter [y/n]')
        
        ans = ask_for_input('y (yes)')
        
        if ans == 'n':
            print("\nI'm sorry")
            print('If you selected the wrong episode you can try again')
            print('Otherwise please contact the developer')
            print('Try again [y/n]')
            ans = ask_for_input('y (try again)')
            
            if ans == 'n':
                return None
            
            return self.ask_for_filter(episodes, title)
        
        return ep_filter
    
    
    def get_show_filter(self, title, link):
        show = Show(title, '', '', link, '')
        episodes = self.get_all_show_episodes(show)
        
        ep_filter = self.ask_for_filter(episodes, title)
        
        if ep_filter == None:
            print('Exiting due to filter creation error')
            exit(1)
        
        return ep_filter
    
