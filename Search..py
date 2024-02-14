import array
from multiprocessing.connection import Connection
import spacy
from Levenshtein import distance
from multiprocessing import Process, cpu_count, Pipe
import math

# print(array.typecodes)

class Search:
    def __init__(self, pool) -> None:
        self.nlp = spacy.load('en_core_web_md')
        self.pool = pool
    
    def search(self, query: str) -> str:
        """
        returns best match from the pool
        """
        work_size = math.ceil(len(self.pool) / cpu_count()/2)
        
        connections = [Pipe()]*cpu_count()*2
        
        workers = [Process(target=self.search_worker, args=(self.pool[start:min(start + work_size, len(self.pool))], query, connections[start//work_size][1])) 
                            for start in range(0, len(self.pool), work_size)]
        
        
        for i in workers:
            i.start()
        
        min_dist, closest_word = connections[0][0].recv()
        workers[0].join()
        
        for i in range(1, len(workers)):
            dist, word = connections[i][0].recv()
            workers[i].join()
            
            if dist < min_dist:
                min_dist = dist
                closest_word = word
                
        return closest_word
    
    
    def search_worker(self, workload, query, conn: Connection) -> tuple[int, str]:
        closest_word = workload[0]
        min_dist = distance(closest_word, query)
        
        for i in workload:
            if i == query:
                conn.send((0, i))
                return
            continue
            
            dis = distance(query, i)
            
            if dis < min_dist:
                min_dist = dis
                closest_word = i
                
                if min_dist == 0:
                    conn.send((min_dist, closest_word))
                    return
        
        conn.send((min_dist, closest_word))

import random
import string


if __name__ == '__main__':
    
    def generate_random_strings(n, length):
        chars = string.ascii_letters + string.digits + string.punctuation
        return [''.join(random.choice(chars) for _ in range(length)) for _ in range(n)]

    # Example usage
    n = 1000
    length = 21
    random_strings = generate_random_strings(n, length)
    # print(random_strings)
    
    print("starting")
    engine = Search(random_strings)


    # print(engine.search(random_strings[67]))
    # print(random_strings[67])
    
    
    for i in random_strings:
        dis =  distance(i, random_strings[-1])
        if dis == 0:
            print(i)
            
    print("done")

