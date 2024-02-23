import array
from multiprocessing.connection import Connection
from Levenshtein import distance
from multiprocessing import Process, cpu_count, Pipe
import math

class SearchEngine:
    def __init__(self) -> None:
        pass
    
    def search(self, query):
        pass
    
    def get_data(self):
        pass
    
    def update_cache(self):
        pass
    
    def load_from_cache(self):
        pass
    
    def write_cache(self):
        pass
    


import random
import string
import time


if __name__ == '__main__':
    
    def generate_random_strings(n, length):
        chars = string.ascii_letters + string.digits + string.punctuation
        return [''.join(random.choice(chars) for _ in range(length)) for _ in range(n)]

    # Example usage
    n = 1000000
    length = 21
    random_strings = generate_random_strings(n, length)
    # print(random_strings)
    
    print("starting")
    engine = Search(random_strings)
    
    tm = time.time()
    print(engine.search(random_strings[-1]))
    print(random_strings[-1])
    print(time.time() - tm)
    
    tm = time.time()
    min_dist = distance(random_strings[0], random_strings[-1])
    for i in random_strings:
        dis = distance(i, random_strings[-1])
        if dis < min_dist:
            min_dist = dis
            closest_word = i
            
            if min_dist == 0:
                print(i)
                break
                
    print(time.time() - tm)
    print("done")

