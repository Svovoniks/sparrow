import json
from typing import List
from Parsers.SubsPleaseParser import SubsPleaseParser, SUBS_PLEASE_PARSER_NAME
from Show import Show
from os.path import exists


CONFIG_FILE = "sys_torrent.cfg"
REQUIRED_CONFIG_FIELDS = ['download_dir', 'show_list']

class Configuration:
    
    def __init__(self, download_dir: str, show_list: list[Show]) -> None:
        self.download_dir = download_dir
        self.show_list = show_list
    
    
    # returns a Configuration object if CONFIG_FILE is valid
    @staticmethod
    def try_parse_config():
        config_json = Configuration.get_config_json()
        
        if config_json == None:
            return None
                
        return Configuration(config_json['download_dir'], [Show.from_json(i) for i in config_json["show_list"] if i != None])
    
    
    # adds show to the show list BUT doesn't save it to the disk
    def add_show(self, show: Show):
        self.show_list.append(show)
    
    
    # builds json object from self
    def build_json(self):
        return {
            "download_dir": self.download_dir,
            "show_list": [i.to_json() for i in self.show_list],
        }
    
    
    # updates config in CONFIG_FILE file
    def update_config(self):
        with open(self.config_location, 'w') as file:
            json.dump(self.build_json(), file)
    
    
    # creates full config in CONFIG_FILE file and returns Configuration 
    @staticmethod
    def create_config(download_dir, show_list):
        config = Configuration(download_dir,  show_list)
        
        with open(CONFIG_FILE) as file:
            json.dump(config.build_json())
            
        return config
    
    
    # checks if all required fields are present in config_json
    @staticmethod
    def check_config_json(config_json):
        return all([field in config_json for field in REQUIRED_CONFIG_FIELDS])
    
    
    # if CONFIG_FILE is a valid config file returns valid config_json
    @staticmethod
    def try_get_config_json():
        if not exists(CONFIG_FILE):
            return None
        
        with open(CONFIG_FILE) as file:
            try:
                config_json = json.load(file)
                
                if Configuration.check_config_json(json.load(file)):
                    return config_json
                
                return None
            except:
                return None
