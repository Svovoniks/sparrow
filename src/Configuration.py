import json

from termcolor import colored
# from typing import List, Self
from src.Parsers.SubsPleaseParser import SubsPleaseParser, SUBS_PLEASE_PARSER_NAME
from src.Parsers.EZTVParser import EZTVParser, EZTV_PARSER_NAME
from src.Parsers.TokyoToshokanParser import TokyoToshokanParser, TOKYO_TOSHOKAN_PARSER_NAME
from src.Show import Show
from os.path import exists


CURRENT_CONFIG_VER = 1
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
    TOKYO_TOSHOKAN_PARSER_NAME: TokyoToshokanParser
}

MAGIC_SEARCH_PARSERS = [
    SUBS_PLEASE_PARSER_NAME,
    EZTV_PARSER_NAME,
]

EXTERNAL_SEARCH_PARSERS = [
    TOKYO_TOSHOKAN_PARSER_NAME,
]

CONFIG_FILE = "sys_torrent.cfg"
REQUIRED_CONFIG_FIELDS = ['download_dir', 'show_list']

SAMPLE_CONFIG = {
    DOWNLOAD_DIR: 'dir',
    SHOW_LIST: [],
}
    

class ConfigUpdater:
    def __init__(self, full_json: dict[str, str]) -> None:
        self.full_json = full_json
    
    def update(self, from_v: int):
        update_map = {
            0: self.update_from_0_to_1,
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

class Configuration:
    
    def __init__(self, full_json: dict[str, str]) -> None:
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
    
    
    # builds json object from self
    def build_json(self):
        return self.config_json
    
    
    # updates config in CONFIG_FILE file
    def update_config(self):
        with open(CONFIG_FILE, 'w') as file:
            json.dump(self.build_json(), file)
    
    
    # creates full config in CONFIG_FILE file and returns Configuration 
    @staticmethod
    def create_config(download_dir):
        config_json =  SAMPLE_CONFIG
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
