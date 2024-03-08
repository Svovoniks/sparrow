from termcolor import colored
import textdistance
import time
from src.Show import Show
from src.Configuration import EXTERNAL_SEARCH_PARSERS, MAGIC_SEARCH_PARSERS, PARSER_DICT, Configuration
from src.utils import ask_for_input, print_colored_list, map_to_columns, verify_num_input

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
        best_match_parser = list(self.data.keys())[0]
        best_match = self.data[best_match_parser][0]
        
        min_dist = textdistance.levenshtein(best_match[0], query)
        
        for parser, show_set in self.data.items():
            for i in show_set:
                dis = textdistance.levenshtein(i[0], query)
                if dis < min_dist:
                    min_dist = dis
                    best_match = i
                    best_match_parser = parser
                    
                    if min_dist == 0:
                        return (parser, best_match)
        
        return (parser, best_match)
    
    def magic_search(self, query, look_in=None):
        tm = time.time()
        
        self.get_data(query, look_in)
        
        if len(self.data) == 0:
            return None
        
        if all(map(lambda a: len(a) == 0, self.data.values())):
            return None
        
        best_match_parser, best_match = self.get_best_match(query)
        
        print(f'Look up time {time.time() - tm:.3f} sec')
        
        print(colored(f'Found "{best_match[0]}" on {best_match_parser}', 'green'))
        print()
        
        parser = PARSER_DICT[best_match_parser]()
        
        show_filter = parser.get_show_filter(*best_match)
        
        return Show(best_match[0], best_match_parser, show_filter, best_match[1])
    
    
    def get_data(self, key, look_in=None):
        if look_in is not None:
            self.data[look_in] = PARSER_DICT[look_in]().get_all_shows(key)
            return
        
        for name in MAGIC_SEARCH_PARSERS:
            self.data[name] = PARSER_DICT[name]().get_all_shows(key)
        

