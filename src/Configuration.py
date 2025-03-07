import json

from termcolor import colored
from src.Parsers.SubsPleaseParser import SubsPleaseParser, SUBS_PLEASE_PARSER_NAME
from src.Parsers.EZTVParser import EZTVParser, EZTV_PARSER_NAME
from src.Parsers.TokyoToshokanParser import TokyoToshokanParser, TOKYO_TOSHOKAN_PARSER_NAME
from src.Parsers.TheRARBGParser import TheRARBGParser, THE_RARBG_PARSER_NAME
from src.Show import Show
from os.path import exists
from src.utils import ask_for_num, print_colored_list
import os


CURRENT_CONFIG_VER = 3
CONFIG_VER = 'config_v'

SCRIPT_LINE = 'script_line'
TMP_FILE = 'tmp_file'
TMP_FILE_STARTER = 'tmp_starter'
DOWNLOAD_DIR = 'download_dir'
SHOW_LIST = 'show_list'
UPDATE_ON_APP_START = 'update_when_app_launched'

PARSER_DICT = {
    SUBS_PLEASE_PARSER_NAME: SubsPleaseParser,
    EZTV_PARSER_NAME: EZTVParser,
    TOKYO_TOSHOKAN_PARSER_NAME: TokyoToshokanParser,
    THE_RARBG_PARSER_NAME: TheRARBGParser
}

MAGIC_SEARCH_PARSERS = [
    SUBS_PLEASE_PARSER_NAME,
    EZTV_PARSER_NAME,
]

EXTERNAL_SEARCH_PARSERS = [
    TOKYO_TOSHOKAN_PARSER_NAME,
    THE_RARBG_PARSER_NAME,
]

CONFIG_FILE = "sys_torrent.cfg"
REQUIRED_CONFIG_FIELDS = ['download_dir', 'show_list']

SAMPLE_CONFIG_WINDOWS = {
    CONFIG_VER: CURRENT_CONFIG_VER,
    DOWNLOAD_DIR: 'dir',
    SHOW_LIST: [],
    SCRIPT_LINE: [2, '@start', '""',  ""],
    TMP_FILE: 'tmp.bat',
}

SAMPLE_CONFIG_LINUX = {
    CONFIG_VER: CURRENT_CONFIG_VER,
    DOWNLOAD_DIR: 'dir',
    SHOW_LIST: [],
    SCRIPT_LINE: [1, 'xdg-open', ''],
    TMP_FILE: 'tmp.sh',
}

class ConfigUpdater:
    def __init__(self, full_json) -> None:
        self.full_json = full_json

    def update(self, from_v: int):
        update_map = {
            0: self.update_from_0_to_1,
            1: self.update_from_1_to_2,
            2: self.update_from_2_to_3,
        }

        while from_v != CURRENT_CONFIG_VER:
            from_v = update_map[from_v]()

        print(colored(f"Updated config version to {from_v}", 'green'))

        with open(CONFIG_FILE, 'w') as file:
            json.dump(self.full_json, file)

        return self.full_json

    def update_from_0_to_1(self):
        self.full_json.update({CONFIG_VER: 1})
        self.full_json.update({'script_line': '@start "" "{}"\n'})
        self.full_json.update({'tmp_file': 'tmp.bat'})
        self.full_json.update({'tmp_starter': ''})
        return 1

    def get_last_episodes(self):
        for i in self.full_json['show_list']:
            show = Show.from_json(i)
            print(colored(f'Updating {show.title}', 'green'))
            parser = PARSER_DICT[show.parser_name]()

            episodes = parser.get_all_show_episodes(show, 200)

            episodes = parser.apply_filter(parser.process_user_filter(show.filter), episodes)

            episodes.append(('None of these', ))

            print_colored_list(episodes, mapper=lambda a: a[0])

            num = ask_for_num('What episode is the last one you have downloaded?',  len(episodes))

            i.update({'last_episode': episodes[num-1][0]})

    def update_from_1_to_2(self):
        backup_file = 'sys_torrent_backup_V2.cfg'

        with open(backup_file, 'w') as file:
            json.dump(self.full_json, file)

        self.full_json.update({CONFIG_VER: 2})

        print('In this update i changed how this app works')
        print('It should work way faster now')
        print('But now i need to store more data than before')
        print('(I need to know the last episode i downloaded for each show)')
        print("And your current config dosen't have it")
        print("There are two ways i can get it")
        print(''' - 1: I can set it to None and wait for next "update all" and that should do it''')
        print(''' - 2: I can ask you for it (i'll help a little)\n''')

        print("I am not a 100% on this one so i'd recommend you try 1 and if that fails 2")
        print(f'Just in case i made a backup in "{backup_file}"')

        num = ask_for_num('What should i do?', 2)


        for show in self.full_json['show_list']:
            show.update({'last_episode': None})

        if num == 2:
            self.get_last_episodes()

        return 2

    def update_from_2_to_3(self):
        backup_file = 'sys_torrent_backup_V2.cfg'

        with open(backup_file, 'w') as file:
            json.dump(self.full_json, file)

        sample = Configuration.get_sample_config()
        self.full_json.update({SCRIPT_LINE: sample[SCRIPT_LINE]})
        self.full_json.update({CONFIG_VER: 3})
        return 3

class Configuration:

    def __init__(self, full_json) -> None:
        config_ver = int(full_json.get(CONFIG_VER, '0'))
        if CURRENT_CONFIG_VER != config_ver:
            full_json = ConfigUpdater(full_json).update(config_ver)

        self.config_json = full_json
        self.show_list = [Show.from_json(i) for i in self.config_json[SHOW_LIST] if i != None]

    def __getitem__(self, arg):
        return self.config_json[arg]

    def __setitem__(self, arg, new_value):
        self.config_json[arg] = new_value

    @staticmethod
    def try_parse_config():
        config_json = Configuration.try_get_config_json()

        if config_json == None:
            return None

        return Configuration(config_json)


    # adds show to the show list BUT doesn't save it to the disk
    def add_show(self, show: Show):
        self.config_json[SHOW_LIST].append(show.to_json())
        self.show_list.append(show)

    def remove_show(self, show: Show):
        self.config_json[SHOW_LIST].remove(show.to_json())
        self.show_list.remove(show)

    def update_show(self, show: Show):
        for idx in range(len(self.config_json[SHOW_LIST])):
            if Show.from_json(self.config_json[SHOW_LIST][idx]) == show:
                self.config_json[SHOW_LIST][idx] = show.to_json()
                return


    # builds json object from self
    def build_json(self):
        return self.config_json


    # updates config in CONFIG_FILE file
    def update_config(self):
        with open(CONFIG_FILE, 'w') as file:
            json.dump(self.build_json(), file)

    @staticmethod
    def get_sample_config():
        if os.name == 'posix':
             return SAMPLE_CONFIG_LINUX
        if os.name == 'nt':
            return SAMPLE_CONFIG_WINDOWS

        print("you appear to be using some weird OS i don't have a config for it so you are gonna have to make it yourself")
        exit(1)


    # creates full config in CONFIG_FILE file and returns Configuration
    @staticmethod
    def create_config(download_dir):
        config_json = Configuration.get_sample_config()
        config_json.update({DOWNLOAD_DIR: download_dir})

        config = Configuration(config_json)

        with open(CONFIG_FILE, 'w') as file:
            json.dump(config.build_json(), file)

        return config


    # checks if all required fields are present in config_json
    @staticmethod
    def check_config_json(config_json):
        return all([field in config_json for field in REQUIRED_CONFIG_FIELDS])


    @staticmethod
    def try_get_config_json():
        if not exists(CONFIG_FILE):
            return None

        config_json = None

        with open(CONFIG_FILE) as file:
            try:
                config_json = json.load(file)
            except:
                return None

        if Configuration.check_config_json(config_json):
            return config_json

        return None

    def __eq__(self, __value) -> bool:
        if __value == None:
            return False

        return all([
            self.config_json == __value.config_json,
            self.show_list == __value.show_list
        ])

    def __repr__(self) -> str:
        return f"show list:{self.show_list}"

