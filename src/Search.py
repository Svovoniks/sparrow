from termcolor import colored
import textdistance
import time
from src.Show import Show
from src.Configuration import EXTERNAL_SEARCH_PARSERS, MAGIC_SEARCH_PARSERS, PARSER_DICT
from src.utils import ask_for_input, ask_for_num, print_colored_list, verify_num_input

class SearchEngine:
    def __init__(self) -> None:
        self.data = {}


    def find_show(self, query):
        print('I can find stuff on:')
        parser_list = [('[Website]', '[Magic search support]')]

        parser_list.extend(list(map(lambda a: (a, "True"), MAGIC_SEARCH_PARSERS)))
        parser_list.extend(list(map(lambda a: (a, "False"), EXTERNAL_SEARCH_PARSERS)))

        print_colored_list(parser_list, first_heading=True)

        print(colored('''ProTip: if website doesn't support "magic search" you will have to select it in order to find something on it''', 'cyan'))
        print()

        print('Do you want me to look somewhere specific?')
        print('If so enter the number of that website')

        look_in = ask_for_input('look everywhere')

        if verify_num_input(look_in, len(parser_list)-1):
            look_in = parser_list[int(look_in)][0]
            print(f'Looking on {look_in}')
        else:
            look_in = None
            print('Looking everywhere')

        if look_in == None or look_in in MAGIC_SEARCH_PARSERS:

            return self.magic_search(query, look_in)

        return PARSER_DICT[look_in]().find_show(query)

    def get_best_match(self, query):
        best_match_parser = None
        best_match = None

        min_dist = None

        for parser, show_set in self.data.items():
            for i in show_set:
                dis = textdistance.levenshtein(i[0].lower(), query.lower())
                if min_dist is None or dis < min_dist:
                    min_dist = dis
                    best_match = i
                    best_match_parser = parser

                    if min_dist == 0:
                        return (best_match_parser, best_match, min_dist)

        return (best_match_parser, best_match, min_dist)

    def magic_search(self, query, look_in=None):
        tm = time.time()

        self.get_data(query, look_in)

        if len(self.data) == 0:
            return None

        if all(map(lambda a: len(a) == 0, self.data.values())):
            return None

        best_match_parser, best_match, min_dist = self.get_best_match(query)

        print(f'Look up time {time.time() - tm:.3f} sec')

        print(colored(f'Found "{best_match[0]}" on {best_match_parser}', 'green'))
        confindence = max(1 - (min_dist / len(best_match[0])), 0)
        if confindence < 0.7:
            print(colored(f'WARNING: low confidence score: {confindence*100:0.1f}%', 'yellow'))
        else:
            print(colored(f'Confidence score: {confindence*100:0.1f}%', 'green'))
        print()

        parser = PARSER_DICT[best_match_parser]()

        show_filter = parser.get_show_filter(*best_match)

        print('Do you want to specifiy what episodes you already have? [y/n]')

        ans = ask_for_input('n (No)')


        show = Show(best_match[0], best_match_parser, show_filter, best_match[1], None)

        if ans == 'y':
            show.last_episode = self.get_last_episode(show)

        return show

    def get_last_episode(self, show: Show):
        parser = PARSER_DICT[show.parser_name]()

        episodes = parser.get_all_show_episodes(show, 200)

        episodes = parser.apply_filter(parser.process_user_filter(show.filter), episodes)
        episodes.append(('None of these',))

        print_colored_list(episodes, mapper=lambda a: a[0])

        num = ask_for_num('What episode is the last one you have downloaded?',  len(episodes))

        return episodes[num-1][0]

    def get_data(self, key, look_in=None):
        if look_in is not None:
            self.data[look_in] = PARSER_DICT[look_in]().get_all_shows(key)
            return

        for name in MAGIC_SEARCH_PARSERS:
            self.data[name] = PARSER_DICT[name]().get_all_shows(key)


