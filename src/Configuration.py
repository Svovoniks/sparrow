import json
# from typing import List, Self
from src.Parsers.SubsPleaseParser import SubsPleaseParser, SUBS_PLEASE_PARSER_NAME
from src.Parsers.EZTVParser import EZTVParser, EZTV_PARSER_NAME
from os.path import exists
from src.Show import Show

DOWNLOAD_DIR = 'download_dir'
SHOW_LIST = 'show_list'
UPDATE_ON_APP_START = 'update_when_app_launched'

PARSER_DICT = {
    SUBS_PLEASE_PARSER_NAME: SubsPleaseParser, 
    EZTV_PARSER_NAME: EZTVParser, 
}

CONFIG_FILE = "sys_torrent.cfg"
REQUIRED_CONFIG_FIELDS = ['download_dir', 'show_list']

SAMPLE_CONFIG = {
    DOWNLOAD_DIR: 'dir',
    SHOW_LIST: [],
}

class Configuration:
    
    def __init__(self, full_json: dict) -> None:
        self.config_json = full_json
        self.show_list: list[Show] = [Show.from_json(i) for i in self.config_json[SHOW_LIST] if i != None]
        
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
