from Parsers.SubsPleaseParser import SUBS_PLEASE_PARSER_NAME, SubsPleaseParser


DOWNLOAD_DIR = 'download_dir'
SHOW_LIST = 'show_list'
CACHE_DIR = 'cache_dir'
USE_CACHE = 'use_cache'
UPDATE_ON_APP_START = 'update_when_app_launched'

PARSER_DICT = {
    SUBS_PLEASE_PARSER_NAME: SubsPleaseParser, 
}

CONFIG_FILE = "sys_torrent.cfg"
REQUIRED_CONFIG_FIELDS = ['download_dir', 'show_list']

SAMPLE_CONFIG = {
    'download_dir': None,
    'show_list': None,
    'cache_dir': 'cache',
    'use_cache': True,
}