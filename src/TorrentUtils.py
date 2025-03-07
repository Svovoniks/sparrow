import sys
import os
import subprocess
from magnet2torrent import Magnet2Torrent
from src.utils import HiddenPrints

class TorrentEngine:
    def __init__(self, script_line) -> None:
        self.script_line = script_line[1:]
        self.magnet_location = script_line[0]
        self.dowonload_list = []


    def add_download(self, magnet: str):
        self.dowonload_list.append(magnet)

    def download(self):
        for magnet in self.dowonload_list:
            if sys.platform == "win32":
                os.startfile(magnet)
            elif sys.platform == "linux":
                ls = self.script_line[:]
                ls[self.magnet_location] = magnet
                subprocess.Popen(ls).wait()

class MagnetChecker:
    def __init__(self, magnet) -> None:
        self.magnet = magnet

    async def get_filename(self):
        m2t = Magnet2Torrent(self.magnet)
        try:
            filename = None
            with HiddenPrints():
                filename, torrent_data = await m2t.retrieve_torrent()
            return filename
        except:
            print("Couldn't check magnet link")

        return None

