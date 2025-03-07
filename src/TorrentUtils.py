import subprocess
from magnet2torrent import Magnet2Torrent
from src.utils import HiddenPrints

class TorrentEngine:
    def __init__(self, script_line, tmp_file, tmp_file_starter) -> None:
        self.script_line = script_line[1:]
        self.magnet_location = script_line[0]
        self.dowonload_list = []


    def add_download(self, magnet: str):
        dw = self.script_line[:]
        dw[self.magnet_location] = magnet
        self.dowonload_list.append(dw)

    def flush_script(self):
        pass

    def download(self):
        self.flush_script()
        for dw in self.dowonload_list:
            subprocess.Popen(dw).wait()

    def clean_up(self):
        pass


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

