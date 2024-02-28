import textdistance

from src.Configuration import PARSER_DICT, Configuration

class SearchEngine:
    def __init__(self) -> None:
        self.data = {}
    
    def find(self, query):
        if self.data == {}:
            self.get_data(query)
        
        if len(self.data) == 0:
            return None
        
        if all(map(lambda a: len(a) == 0, self.data.values())):
            return None
        
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
                    
        
        return (best_match_parser, best_match)

    def get_data(self, key, look_in=None):
        if look_in != None:
            self.data[look_in] = PARSER_DICT[look_in]().get_all_shows(key)
            return
        
        for name, cls in PARSER_DICT.items():
            self.data[name] = cls().get_all_shows(key)
        

