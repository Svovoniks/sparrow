from functools import reduce
from os.path import isdir
from termcolor import colored
import time

from src.Show import Show
from src.ShowManager import ShowManager
from src.TorrentUtils import TorrentEngine
from src.Search import SearchEngine
from src.utils import ask_for_num, print_colored_list, ask_for_input, verify_num_input
from src.Configuration import SCRIPT_LINE, TMP_FILE, TMP_FILE_STARTER, Configuration, PARSER_DICT
class UI:
    def __init__(self, config) -> None:
        self.config: Configuration = config
        self.show_manager: ShowManager = ShowManager(config)

    @staticmethod
    def start(args):
        ui = UI.setup_UI()

        screen_map = {
            'update': ui.update_all,
        }

        if len(args) == 1:
            screen_map.get(args[0], ui.main_screen)()
        else:
            ui.main_screen()

    def main_screen(self):
        screen_list = [
            ('update', 'update all shows', self.update_all),
            ('add', 'add show', self.add_show),
            ('remove', 'remove show', self.remove_show),
            ('list', 'list tracked shows', self.list_shows_screen),
        ]

        screens_map = {}

        for idx, el_tp in enumerate(screen_list):
            screens_map[str(idx+1)] = el_tp[2]
            screens_map[el_tp[0]] = el_tp[2]

        print('You can:')

        print_colored_list(screen_list, mapper=lambda a: a[1])
        print("What do you want?\nEnter number or the first word of the action you want to perform")

        next_screen = ask_for_input('exit')

        print()

        screens_map.get(next_screen, exit)()

        print()

        self.main_screen()


    def list_shows_screen(self):
        print('Your show list:')

        self.list_shows()

        print("Did you get a good look?\nI'm waiting for you to hit that Enter")

        ask_for_input('main screen')


    def list_shows(self):
        mx_title_len = len(max(self.config.show_list, key=lambda show: len(show.title), default=Show('','','','', '')).title)

        print_colored_list(self.config.show_list, mapper=lambda show: ('{0:' + str(mx_title_len) + '}').format(show.title)
                            + f' [Source: {show.parser_name}]')

    def update_all(self):
        updates = self.show_manager.check_for_updates()

        if len(updates) == 0:
            print("Everything seems to be up to date")
            return

        torrent_engine = TorrentEngine(
            self.config[SCRIPT_LINE],
            self.config[TMP_FILE],
            self.config[TMP_FILE_STARTER]
        )

        print('Staging updates')
        for i in updates:
            torrent_engine.add_download(i)

        print('Starting downloading')
        torrent_engine.download()
        torrent_engine.clean_up()

    def add_show(self):
        print('Enter name of the show you want to add')
        show_name = ask_for_input('get confused')

        if show_name == '':
            print('Name is empty\nDo you want to try again [y/n]')
            if ask_for_input('n (main screen)') == 'y':
                self.add_show()
            return

        engine = SearchEngine()

        show = engine.find_show(show_name)

        if show == None:
            print(colored("Search didn't return any results", 'red'))
            return

        if show in self.config.show_list:
            print(colored('This show was already in you list', 'red'))
            return

        self.config.add_show(show)
        self.config.update_config()

        print(colored(f'Added: "{show.title}"', 'green'))

    def remove_show(self):
        self.list_shows()

        to_delete = ask_for_num("Choose show to delete\nEnter number that corresponds to the show", len(self.config.show_list))

        print(colored(f'Deleted: "{self.config.show_list[to_delete-1].title}"', 'red'))

        self.config.remove_show(self.config.show_list[to_delete-1])
        self.config.update_config()

    @staticmethod
    def ask_for_config():
        print("I couldn't find a config file")
        print("So let's get you started")
        print("Where would you like me to put new episodes?")

        download_dir = ask_for_input('ask again')

        while not isdir(download_dir):
            print(colored("Error: not a real folder", 'red'))
            print("Try again")

            download_dir = ask_for_input('ask again')

        config = Configuration.create_config(download_dir)

        print(colored("You are all set", 'green'))
        print(colored("Please don't remove last episode of each show", 'green'))
        print(colored("So i know what you've watched already", 'green'))
        return config


    @staticmethod
    def setup_UI():
        config = Configuration.try_parse_config()

        if config == None:
            config = UI.ask_for_config()

        return UI(config)
