import re
import subprocess
from magnet2torrent import Magnet2Torrent
from os import remove
from os.path import exists, join
from src.utils import HiddenPrints

class TorrentEngine:
    def __init__(self, script_line, tmp_file, tmp_file_starter) -> None:
        self.script_line = script_line
        self.script = ""
        self.tmp_file = tmp_file
        while exists(self.tmp_file):
            self.tmp_file = 'new' + self.tmp_file

        self.start_command = filter(lambda a: a != '', [tmp_file_starter, self.tmp_file])

    def add_download(self, magnet: str):
        self.script += self.script_line.format(magnet)

    def flush_script(self):
        with open(self.tmp_file, 'w') as file:
            file.write(self.script)

    def download(self):
        self.flush_script()
        subprocess.Popen(self.start_command).wait()

    def clean_up(self):
        remove(self.tmp_file)


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

