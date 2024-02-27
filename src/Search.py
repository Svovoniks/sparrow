import array
from os import listdir
from multiprocessing.connection import Connection
from Levenshtein import distance
from multiprocessing import Value, Process, cpu_count, Pipe, Manager
import math
# import spacy
import textdistance

from src.Configuration import PARSER_DICT, Configuration

class SearchEngine:
    def __init__(self) -> None:
        self.data = {}
    
    def find(self, query):
        if self.data == {}:
            self.get_data()
        
        if len(self.data) == 0:
            return None
        
        best_match_parser = list(self.data.keys())[0]
        best_match = self.data[best_match_parser][0]
        
        
        # min_dist = distance(best_match[0], query)
        # min_dist = nlp(best_match[0]).similarity(query_n)
        min_dist = textdistance.levenshtein(best_match[0], query)
    
        # for parser, show_set in self.data.items():
        #     for i in show_set:
        #         dis = distance(i[0], query)
        #         if dis < min_dist:
        #             min_dist = dis
        #             best_match = i
        #             best_match_parser = parser
        #             print(i[0])
        #             print(dis)
                    
        #             if min_dist == 0:
        #                 return (parser, best_match)
        # for parser, show_set in self.data.items():
        #     for i in show_set:
        #         # print(i[0])
        #         dis = query_n.similarity(nlp(i[0]))
        #         if dis > min_dist:
        #             min_dist = dis
        #             best_match = i
        #             best_match_parser = parser
        #             # print(i[0])
        #             # print(dis)
                    
        #             if min_dist == 1:
        #                 return (parser, best_match)
                    
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

    def get_data(self, look_in=None):
        if look_in != None:
            self.data[look_in] = PARSER_DICT[look_in]().get_all_shows()
            return
        
        for name, cls in PARSER_DICT.items():
            self.data[name] = cls().get_all_shows()
        

