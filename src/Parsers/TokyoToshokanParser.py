
import requests
from termcolor import colored
import re
from src.Show import Show

from src.Parsers.ParserBase import ParserBase
from src.utils import ask_for_num, print_colored_list, ask_for_input

TOKYO_TOSHOKAN_PARSER_NAME = 'TokyoToshokan'


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
        episodes = self.get_all_show_episodes(show.title)
        
        to_download = []
        
        for episode in self.apply_filter(self.process_user_filter(show.filter), episodes):
            if episode[0] in download_folder_contents:
                return to_download
            
            print(f'Missing "{episode[0]}"')
            to_download.append(episode[1])
        
        return to_download
    
    def get_all_episodes_from_page(self, page, episodes, limit=None):
        pattern = '''<td class="desc-top"><a href="([^"]+)"><span class="sprite_magnet"></span></a> <a rel="nofollow" type="application/x-bittorrent" href="[^"]+">([^<]+)<span class="s"> </span>([^<]+)</a></td>'''
        
        found = 0
        
        for i in re.findall(pattern, page.text):
            if limit != None and limit <= len(episodes):
                break
            
            found += 1
            episodes.append((i[1] + i[2], i[0]))
        
        return found
    
    
    def get_all_shows(self):
        return []
    
    def get_all_show_episodes(self, key, limit=200):
        """
        Returns:
            list[list[str]]: list of all episodes found for the given key
            if the form of [(episode1_name, episode1_magnet_link), ...]
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
    
    def preprocess_title(self,  title):
        return title.replace('[', '').replace(']', '').replace('(', '').replace(')', '').replace('\\', '')
    
    def process_user_filter(self, _filter):
        real_rgx = r'.*'

        user_rgx = r'<<[^(>>)]+>>'

        full_re = r''
        
        split_list = re.split(user_rgx, _filter)
        
        if len(split_list) == 0:
            return full_re
        
        for i in split_list:
            if i == '':
                continue
            
            full_re += self.preprocess_title(i) + real_rgx
        
        return full_re
    
    def apply_filter(self, real_filter, episodes):
        return list(filter(lambda a: re.fullmatch(real_filter, self.preprocess_title(a[0])) !=  None, episodes))
            
    def get_filter(self, title, episodes):
        print('This website is an aggregator of shows from multiple sources')
        print("And each source has it's own naming scheme")
        print("To solve this problem we would need an AI, or a separate parser for each source")
        print("Spoiler: This programm is none of those things")
        print("So we are going to have to outsourse this task to some external AI, an AGI perhaps")
        print("As you may have guessed, we are going to use you")
        print()
        print("Here is what you have to do:")
        print(f'1. Look at this filename "{colored(title, "green")}"')
        print(f'2. Encase parts of it that can change from one episode to the next like this: <<{colored("variable", "green")}>>')
        print()
        print(f'''For example if filename is {colored('"[SubsPlease] Metallic Rouge - 08 (1080p) [19D9D43F].mkv"', 'cyan')} than''')
        print(f'''You should change it to {colored('"[SubsPlease] Metallic Rouge - <<08>> (1080p) <<[19D9D43F]>>.mkv"', 'cyan')}''')
        print('''And don't type ""''')
        
        
        ok = False
        user_filter = None
        
        while not ok:
            user_filter = ask_for_input('empty filter (matches nothing)')
            
            processed_filter = self.process_user_filter(user_filter)
            
            print('\nAfter applying the filter only these episodes remain:')
            
            print_colored_list(self.apply_filter(processed_filter, episodes), mapper=lambda a: a[0])
            
            print('Is that correct?')
            print('Enter [y/n]')
        
            ans = ask_for_input('y (yes)')
            
            if ans == 'n':
                print('Do you want to try again [y/n]')
                ans = ask_for_input('y (try again)')
                
                if ans == 'n':
                    return None
                
                continue
            
            ok = True
        
        return user_filter
    
    def get_show_filter(self, title, link):
        episodes = self.get_all_show_episodes(title)
        
        if len(episodes) == 0:
            print(colored(f'''"{title}" doesn't have any episodes at the moment''', 'red'))
            print(colored(f"So i can't create a show filter right now, plese try again later", 'red'))
            print(colored(f"Exiting", 'red'))
            exit(1)
        
        print(f'Here is a list of all episode for {title}')
        
        print_colored_list(episodes, mapper=lambda a: a[0])
        
        ep_num = ask_for_num('\nPlease eneter the number of the episode from which you want to create episode filter\n', len(episodes))
        
        ep_filter = self.get_filter(episodes[ep_num-1][0], episodes)
        
        if ep_filter != None:
            return ep_filter
        
        return None
    
    def find_show(self, query):
        link = self.search_url.format(self.process_key(query))
        show_filter = self.get_show_filter(query, link)
        
        if show_filter == None:
            return None
        
        return Show(query, TOKYO_TOSHOKAN_PARSER_NAME, show_filter, link)

