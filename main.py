from Parsers.SubsPleaseParser import SubsPleaseParser
from UI import UI

CONFIG_FILE = "sys_torrent.cfg"
REQUIRED_CONFIG_FIELDS = ['download_dir', 'title_list']
PARSER_MAP = {
    "subsPlease": SubsPleaseParser
}

if __name__ == "__main__":
    UI.start()


