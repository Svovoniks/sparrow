import re
import subprocess
from magnet2torrent import Magnet2Torrent
from os import remove
from random import randint
from os.path import exists
from src.utils import HiddenPrints

class TorrentEngine:
    def __init__(self, script_line, tmp_file, tmp_file_starter) -> None:
        self.script_line = script_line
        self.script = ""
        self.tmp_file = tmp_file
        while exists(self.tmp_file):
            self.tmp_file = str(randint(0, 10)) + self.tmp_file
            
        self.start_command = f"{tmp_file_starter} .\\{self.tmp_file}".strip()
        
    def add_download(self, magnet: str):
        self.script += self.script_line.format(magnet)
    
    def flush_script(self):
        with open(self.tmp_file, 'w') as file:
            file.write(self.script) 
    
    def download(self):
        self.flush_script()
        subprocess.run(self.start_command)
        
    def clean_up(self):
        remove(self.tmp_file)


class MagnetChecker:
    def __init__(self, magnet) -> None:
        self.magnet = magnet
        
    async def get_filename(self):
        m2t = Magnet2Torrent(self.magnet)
        try:
            with HiddenPrints():
                filename, torrent_data = await m2t.retrieve_torrent()
                return filename
        except:
            print("Couldn't check magnet link")
        
        return None

