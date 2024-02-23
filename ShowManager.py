from os import listdir
from Configuration import DOWNLOAD_DIR, Configuration
from Parsers.ParserFactory import PARSER_MAP


class ShowManager:
    def __init__(self, config: Configuration) -> None:
        self.config = config
        
    def check_for_updates(self) -> list[str]:
        """
        returns list of magnet links for new episodes for tracked shows
        """
        downloaded = listdir(self.config[DOWNLOAD_DIR])
        
        to_download = []
        
        for i in self.config.show_list:
            print(f'checking {i.title}')
            updates = i.check_for_updates(downloaded)
            
            if len(updates) > 0:
                print(f'Found {len(updates)} new episodes')
                to_download.extend(updates)
            else:
                print(f'{i.title} is already up to date')
        
        return to_download
    
    @staticmethod
    def find_show(title: str):
        for i in PARSER_MAP.values():
            i.get_all_show_titles()