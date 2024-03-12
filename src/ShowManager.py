from os import listdir
from src.Configuration import DOWNLOAD_DIR, Configuration, PARSER_DICT


class ShowManager:
    def __init__(self, config: Configuration) -> None:
        self.config = config
        
    def check_for_updates(self):
        """
        returns list of magnet links for new episodes for tracked shows
        """
        to_download = []
        
        for i in self.config.show_list:
            print(f'checking "{i.title}"')
            pr_len = len(to_download)
            last_episode = PARSER_DICT[i.parser_name]().check_show(i, to_download)
            
            new_episodes = len(to_download) - pr_len
            
            if new_episodes > 0:
                print(f'Episodes found: {new_episodes}')
                i.last_episode = last_episode
                self.config.update_show(i)
            else:
                print(f'"{i.title}" is already up to date')
        
        self.config.update_config()
        return to_download
    
    @staticmethod
    def find_show(title: str):
        for i in PARSER_DICT.values():
            i.get_all_show_titles()