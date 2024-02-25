from os.path import isdir
from termcolor import colored

from src.Configuration import Configuration, PARSER_DICT
from src.Show import Show
from src.ShowManager import ShowManager
from src.TorrentUtils import TorrentEngine
from src.Search import SearchEngine

class UI:
    def __init__(self, config) -> None:
        self.config: Configuration = config
        self.show_manager: ShowManager = ShowManager(config)
    
    @staticmethod
    def start():
        ui = UI.setup_UI()
        ui.main_screen()        
    
    def main_screen(self):
        print("You can:")
        print("1: update all")
        print("2: add new show")
        print("3: remove show")
        print("4: list tracked shows")
        print("[default]: exit")
        
        screens_map = {
            '1': self.update_all,
            'update': self.update_all,
            '2': self.add_show,
            'add': self.add_show,
            '3': self.remove_show,
            'remove': self.remove_show,
            '4': self.list_shows,
            'list': self.list_shows,
        }
        
        next_screen = input("What do you want?\nEnter a number or the first word of desired action\n").strip()
        
        print()
        
        screens_map.get(next_screen, exit)()
        
        print()
        
        self.main_screen()
        
    
    def list_shows(self):
        print('Your show list:')
        print("_______________________")
        for idx, show in enumerate(self.config.show_list):
            print(colored(f'{idx+1}. {show.title} [Source: {show.parser_name}]', 'cyan'))
        
        print("_______________________")
    
    def update_all(self):
        updates = self.show_manager.check_for_updates()
        
        if len(updates) == 0:
            print("Everything seems to be up to date")
            return
        
        torrent_engine = TorrentEngine()
        
        
        print('Queueing updates')
        for i in updates:
            torrent_engine.add_download(i)
        
        print('Starting downloading')
        torrent_engine.download()
        torrent_engine.clean_up()
    
    def add_show(self):
        show_name = input('Enter name of the show you want to add: ')
        if show_name == '':
            if input('Name is empty\nDo you want to try again [y/n]: ') == 'y':
                self.add_show()
            return
        
        engine = SearchEngine()
        
        import time
        
        engine.get_data()
        tm = time.time()
        
        search_result = engine.find(show_name)
        if search_result == None:
            print("Search didn't return any results")
            return
        print(f'time {time.time() - tm}')
        parser_name, closest_match = search_result
        
        print(f'Found "{closest_match[0]}" on {parser_name}')
        
        parser = PARSER_DICT[parser_name]()
        
        show_filter = parser.get_show_filter(*closest_match)
        
        show = Show(closest_match[0], parser_name, show_filter, closest_match[1])
        
        if show in self.config.show_list:
            print(colored('This show was already in you list', 'red'))
            return
        
        self.config.add_show(show)
        self.config.update_config()
        
        print(f'Added: "{show.title}"')
    
    def remove_show(self):
        self.list_shows()
        to_delete = input("Choose show to delete\nEnter number that corresponds to the show: ")
        
        if to_delete.isdigit(): 
            to_delete = int(to_delete)
        else:
            to_delete = -1
        
        while to_delete-1 >= len(self.config.show_list) or to_delete < 0:
            print(colored("I beg your pardon?", 'red'))
            to_delete = input("Choose show to delete\nEnter number that corresponds to the show: ")
            
            if to_delete.isdigit(): 
                to_delete = int(to_delete)
            else:
                to_delete = -1
        
        
        print(f'Deleted: "{self.config.show_list[to_delete-1].title}"')
        
        self.config.remove_show(self.config.show_list[to_delete-1])
        self.config.update_config()
        
    @staticmethod
    def ask_for_config():
        print("I couldn't find a config file")
        print("So let's get you started")        
        print("Where would you like me to put new episodes?")
        
        download_dir = str(input())
        
        while not isdir(download_dir):
            print("Error: not a real folder")
            print("Try again")
            
            download_dir = str(input())
        
        config = Configuration.create_config(download_dir)
        
        print("You are all set")
        print("Please don't remove last episode of each show")
        print("so i know what you've watched already")
        return config
    
    
    @staticmethod
    def setup_UI():
        config = Configuration.try_parse_config()
        
        if config == None:
            config = UI.ask_for_config()
            
        return UI(config)
    
# UI(None).add_show()