import re
from termcolor import colored
from src.Parsers.ParserBase import ParserBase
from src.Show import Show
from src.utils import ask_for_input, ask_for_num, print_colored_list

class NonMagicParserBase(ParserBase):
    '''
    to use this as a superclass you need to implement:
        - "get_all_show_episodes"
        - "process_query"
        - "get_magnet_and_filename"
    and set class variable "parser_name"
    '''
    def __init__(self) -> None:
        super().__init__()
        self.parser_name = 'NonMagicParserBase'
        
        
    def get_magnet_and_filename(self, episode):
        '''
        returns magnet link for a given episode (the "get_all_show_episodes" return tuple)
        '''
        raise NotImplementedError
    
    def check_show(self, show: Show, download_folder_contents):
        episodes = self.get_all_show_episodes(show.title, show.link)
        
        to_download = []
        
        for episode in self.apply_filter(self.process_user_filter(show.filter), episodes):
            
            ans = self.get_magnet_and_filename(episode)
            
            if ans is None:
                continue
            
            magnet, filename = ans
            if filename in download_folder_contents:
                return to_download
            
            print(f'Missing "{episode[0]}"')
            to_download.append(magnet)
        
        return to_download
    
    
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
            
            full_re += re.escape(i) + real_rgx
        
        return full_re
    
    
    def apply_filter(self, real_filter, episodes):
        return list(filter(lambda a: re.fullmatch(real_filter, (a[0])) !=  None, episodes))
            
    def get_filter(self, title, episodes):
        print('This website is an aggregator of shows from multiple sources')
        print("And each source has it's own naming scheme")
        print("To solve this problem we would need an AI, or a separate parser for each source")
        print("Spoiler: This program is none of those things")
        print("So we are going to have to outsource this task to some external AI, an AGI perhaps")
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
            
            print_colored_list(self.apply_filter(processed_filter, episodes), mapper=lambda a: (a[0], a[2]))
            
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
    
    def get_all_show_episodes(self, title, link, limit=200):
        '''
        return a list of all episodes that satisfy user query as a list[(filename, link_to_episode_page, file_size), ...]
        the length of the list shouldn't exceed limit unless it's set to None
        '''
        raise NotImplementedError
    
    def get_show_filter(self, title, link):
        episodes = self.get_all_show_episodes(title, link)
        
        if len(episodes) == 0:
            print(colored(f'''"{title}" doesn't have any episodes at the moment''', 'red'))
            print(colored(f"So i can't create a show filter right now, please try again later", 'red'))
            print(colored(f"Exiting", 'red'))
            exit(1)
        
        print(f'Here is a list of all episode for {title}')
        
        print_colored_list(episodes, mapper=lambda a: (a[0], a[2]))
        
        ep_num = ask_for_num('\nPlease enter the number of the episode from which you want to create episode filter\n', len(episodes))
        
        ep_filter = self.get_filter(episodes[ep_num-1][0], episodes)
        
        if ep_filter != None:
            return ep_filter
        
        return None
    
    def process_query(self, query):
        '''
        turns user "query" into a valid url for a show on the website that parser works with
        '''
        raise NotImplementedError
    
    def find_show(self, query):
        link = self.process_query(query)
        show_filter = self.get_show_filter(query, link)
        
        if show_filter == None:
            return None
        
        return Show(query, self.parser_name, show_filter, link)