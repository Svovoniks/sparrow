from threading import Thread
from copy import deepcopy
from src.Configuration import DOWNLOAD_DIR, Configuration, PARSER_DICT
import time

class ShowManager:
    def __init__(self, config: Configuration) -> None:
        self.config = config

    def check_one(self, show, res):
        print(f'checking "{show.title}"')
        to_download = []
        last_episode = PARSER_DICT[show.parser_name]().check_show(show, to_download)

        new_episodes = len(to_download)

        if new_episodes > 0:
            print(f'Episodes found for "{show.title}": {new_episodes}')
            show.last_episode = last_episode
        else:
            print(f'"{show.title}" is already up to date')

        res[0] = to_download



    def check_for_updates(self):
        """
        returns list of magnet links for new episodes for tracked shows and a new config
        """
        to_download = []
        new_config = deepcopy(self.config)

        # for i in new_config.show_list:
        #     print(f'checking "{i.title}"')
        #     pr_len = len(to_download)
        #     last_episode = PARSER_DICT[i.parser_name]().check_show(i, to_download)
        #
        #     new_episodes = len(to_download) - pr_len
        #
        #     if new_episodes > 0:
        #         print(f'Episodes found: {new_episodes}')
        #         i.last_episode = last_episode
        #         new_config.update_show(i)
        #     else:
        #         print(f'"{i.title}" is already up to date')

        updates = []
        threads  = []
        for i in range(len(new_config.show_list)):
            if i != 0:
                time.sleep(0.2)
            updates.append([None])
            threads.append(Thread(target=self.check_one, args=[new_config.show_list[i], updates[-1]]))
            threads[-1].start()

        for i in range(len(new_config.show_list)):
            threads[i].join()
            to_download.extend(updates[i][0])
            new_config.update_show(new_config.show_list[i])

        print(f"Total found: {len(to_download)}")

        return to_download, new_config

    @staticmethod
    def find_show(title: str):
        for i in PARSER_DICT.values():
            i.get_all_show_titles()
