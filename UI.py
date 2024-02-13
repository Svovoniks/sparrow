from os.path import isdir
from ConfigManager import Configuration

class UI:
    
    def __init__(self, config) -> None:
        self.config = config
    
    @staticmethod
    def start():
        ui = UI.setup_UI()
        
    
    def main_screen(self):
        print("You can:")
        print("1. update all")
        print("2. add new show")
        print("3. remove show")
    
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
        
        Configuration.create_config(download_dir, [])
        
        print("You are all set")
        print("Please don't remove last episode of each show")
        print("so i know what you've watched already")
    
    
    @staticmethod
    def setup_UI(self):
        config = Configuration.try_parse_config()
        
        if config == None:
            config = UI.ask_for_config()
            
        return UI(config)
   