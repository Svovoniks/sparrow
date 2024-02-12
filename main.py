import requests
import re
import os
import asyncio
import subprocess
import json
from os import listdir
from os.path import exists, isdir

from magnet2torrent import Magnet2Torrent, FailedToFetchException

CONFIG_FILE = "sys_torrent.cfg"
REQUIRED_CONFIG_FIELDS = ['download_dir', 'title_list']

class UI:
    
    def __init__(self, config) -> None:
        self.config = config
    
    @staticmethod
    def start():
        ui = UI.setup_UI()
        
        
    
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

class Configuration:
    
    def __init__(self, download_dir, title_list) -> None:
        self.download_dir = download_dir
        self.title_list = title_list
    
    
    # returns a Configuration object if CONFIG_FILE is valid
    @staticmethod
    def try_parse_config():
        config_json = Configuration.get_config_jscn()
        
        if config_json == None:
            return None
                
        return Configuration(config_json['download_dir'], config_json['title_list'])
    
    
    # adds title to the title list BUT doesn't save it to the disk
    def add_tile(self, title_name):
        self.title_list.apppend(title_name)
    
    
    # builds json object from self
    def build_json(self):
        return {
            "download_dir": self.download_dir,
            "title_list": self.title_list,
        }
    
    
    # updates config in CONFIG_FILE file
    def update_config(self):
        with open(self.config_location, 'w') as file:
            json.dump(self.build_json(), file)
    
    
    # creates full config in CONFIG_FILE file and returns Configuration 
    @staticmethod
    def create_config(download_dir, title_list):
        config = Configuration(download_dir,  title_list)
        
        with open(CONFIG_FILE) as file:
            json.dump(config.build_json())
            
        return config
    
    
    # checks if all required fields are present in config_json
    @staticmethod
    def check_config_json(config_json):
        return all([field in config_json for field in REQUIRED_CONFIG_FIELDS])
    
    
    # if CONFIG_FILE is a valid config file returns valid config_json
    @staticmethod
    def try_get_config_jscn():
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



class TorrentEngine:
    def __init__(self) -> None:
        self.script_line = 'start "{}"\n'
        self.script = ""
        self.tmp_file = "tmp.ps1"
        self.start_command = f"powershell.exe .\\{self.tmp_file}"
        
    def add_download(self, magnet):
        self.script += self.script_line.format(magnet)
    
    def flush_script(self):
        with open(self.tmp_file, 'w') as file:
            file.write(self.script) 
    
    def download(self):
        self.flush_script()
        subprocess.run(self.start_command)



class MagnetChecker:
    def __init__(self, magnet) -> None:
        self.magnet = magnet
        
    async def get_filename(self):
        m2t = Magnet2Torrent(self.magnet)
        try:
            filename, torrent_data = await m2t.retrieve_torrent()
            return filename
        except:
            print('Couldnt check magnet link')
        
        return None



class TitleCheckResult:
    def __init__(self) -> None:
        self.pages = []
        self.parser = None



class ParserInterface:
    def __init__(self, download_folder_contents) -> None:
        self.parser_name = 'Default'
        self.download_folder_contents = download_folder_contents

    def check_title(self, title):
        pass
    
    def load_page(self, url):
        resp = requests.get(url)
        
        if resp.status_code != 200:
            print(f"Couldnt load {self.parser_name}")
            return None
        
        return resp



class SubsPleaseParser(ParserInterface):
    def __init__(self, download_folder_contents) -> None:
        super().__init__(download_folder_contents)
        self.parser_name = 'SubsPlease'
        self.search_url = 'https://subsplease.org/shows/'
        self.api_url = 'https://subsplease.org/api/?f=show&tz=Europe/Moscow&sid={}'

    def get_title_page_sublink(self, exact_title):
        pattern = r"""<div class="all-shows-link"><a href="([^"]+)" title="([^"]+)">([^<]+)</a>"""
        
        resp = self.load_page(self.search_url)
        
        if resp == None:
            return None
        
        for i in re.findall(pattern, resp.text):
            print(i)
            if i[1] == exact_title:
                return i[0]
        
        return None
    
    def get_sid(self, title_page):
        page = self.load_page(title_page)
        
        if page == None:
            return res
        
        pattern = r'sid="(\d+)"'
        
        found = re.search(pattern, page.text)
        
        if found == None:
            return None
        
        return found[1]
    
    
    def get_magnets(self, title_page):
        sid = self.get_sid(title_page)
        
        res = []
        
        if sid == None:
            return res
        
        api_resp = self.load_page(self.api_url.format(sid))
        
        if api_resp == None:
            return res
        
        pattern = r'{"res":"1080","torrent":"[^"]+","magnet":"([^"]+)","xdcc":"[^"]+"}]}'
        
        print(api_resp.text)
        
        for i in re.findall(pattern, api_resp.text):
            res.append(i)
            
        return res
        
    
    def check_title(self, title):
        title_page = self.get_title_page_sublink(title)
        
        if title_page == None:
            return False
        
        magnets = self.get_magnets(self.search_url + title_page[1:])
        
        to_download = []
        
        for i in magnets:
            filename = asyncio.run(MagnetChecker(i).get_filename())[:-8]
            
            if filename in self.download_folder_contents:
                return to_download
            
            to_download.append(i)
            
        return to_download



# if __name__ == "__main__":
#     to_download = SubsPleaseParser(listdir(r"C:\Users\svovo\Desktop")).check_title("Yuusha ga Shinda!")
    
#     engine = TorrentEngine()
    
#     for i in to_download:
#         engine.add_download(i)
        
#     engine.download()


