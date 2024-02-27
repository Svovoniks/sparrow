import asyncio
from src.Parsers.ParserBase import ParserBase
import re
from functools import reduce
from src.Show import Show
from src.TorrentUtils import MagnetChecker

from src.utils import ask_for_num

EZTV_PARSER_NAME = 'EZTV'

class EZTVParser(ParserBase):
    def __init__(self) -> None:
        super().__init__()
        self.main_url = 'https://eztvx.to/'
        self.all_shows_url = 'https://eztvx.to/showlist/'
        self.episode_num_pattern = r'(S\d\dE\d\d)'
        
    def check_show(self, show: Show, download_folder_contents: set[str]) -> list[str]:
        show_page = self.load_page(show.link)
        episodes = self.get_all_show_episodes(show_page)
        
        to_download = []
        
        for idx in self.apply_filter(episodes, show.filter):
            
            magnet = self.get_magnet(self.main_url + episodes[idx][0])
            
            filename = asyncio.run(MagnetChecker(magnet).get_filename())
            
            if filename == None: continue
            
            filename = filename[:-14]
            
            if filename in download_folder_contents:
                return to_download
            
            print(f'Missing "{filename}"')
            to_download.append(magnet)
        
        return to_download
    
    def get_magnet(self, episode_link):
        pattern = r'''<a href="([^"]+)" title="Magnet Link">'''
        page = self.load_page(episode_link)
        
        return re.search(pattern, page.text)[1]
        
    
    def get_all_shows(self) -> list[list[str]]:
        """
        Returns:
            list[list[str]]: list of all shows on the site available on the site
            if the form of [[title1, link_to_the_show_page], [title2, link_to_the_show_page]]
        """
        page = self.load_page(self.all_shows_url)
        pattern = r'''<td class="forum_thread_post"><a href="([^"]+)" class="thread_link">([^"]+)</a></td>'''
        
        if page == None:
            return None
        
        return [(i[1], self.main_url + i[0]) for i in re.findall(pattern, page.text)]
    
    
    def get_all_show_episodes(self, page):
        '''
        returns list of all episodes found on the given page in the format of [(sub_link_to_the_episode, episode_name_, episode_file_size), (...)]
        '''
        pattern = r'''<a href="([^"]+)" title="[^"]+" alt="([^"]+)\([^"]+" class="epinfo">[^"]+</a>\n</td>\n<td align="center" class="forum_thread_post">([^"]+)</td>'''
        
        all_episodes = []
        
        for i in re.findall(pattern, page.text):
            all_episodes.append(i)
        
        return all_episodes
    
    def print_all_episodes(self, all_episodes, ep_filter=None):
        # print(all_episodes)
        mx_name_len, mx_size_len = map(len, reduce(lambda tp1, tp2: (None, max(tp1[1], tp2[1], key=len), max(tp1[2], tp2[2], key=len)), all_episodes, (None, '', ''))[1:])
        
        filter_list = None
        
        if ep_filter != None:
            filter_list = self.apply_filter(all_episodes, ep_filter)
        else:
            filter_list = range(len(all_episodes))
        
        for idx in filter_list:
            print((f'{idx+1}. ' + '{1:' + str(mx_name_len) + '}   {2:' + str(mx_size_len) + '}').format(*all_episodes[idx]))
    
    def get_filter(self, ep_title):
        return re.sub(self.episode_num_pattern, '<<episode_number>>', ep_title)
    
    def apply_filter(self, episode_list, ep_filter):
        '''
        returns list of indexes of elements that satisfy ep_filter
        '''
        return [idx for idx, el in enumerate(episode_list) if self.get_filter(el[1]) == ep_filter]
    
    
    def ask_for_filter(self, episodes, title):
        
        print(f'Here is a list of all episode for {title}')
        self.print_all_episodes(episodes)
        
        ep_num = ask_for_num('\nPlease eneter the number of the episode from which you want me to create episode filter\n', len(episodes))
        
        ep_filter = self.get_filter(episodes[ep_num-1][1])
        
        print('\nAfter applying the filter only these episodes remain:')
        
        self.print_all_episodes(episodes, ep_filter)
        
        print('Is that correct?')
        
        ans = input('Enter [y/n] (default: yes) :')
        
        if ans == 'n':
            print("\nI'm sorry")
            print('If you selected the wrong episode you can try again')
            print('Otherwise please contact the developer')
            ans = input('Try again [y/n] (default: yes) :')
            if ans == 'n':
                return None
            
            return self.ask_for_filter(episodes, title)
        
        return ep_filter
    
    
    def get_show_filter(self, title, link):
        page = self.load_page(link)
        
        episodes = self.get_all_show_episodes(page)
        
        ep_filter = self.ask_for_filter(episodes, title)
        
        if ep_filter == None:
            print('Exiting due to filter creation error')
            exit(1)
        
        return ep_filter
    

