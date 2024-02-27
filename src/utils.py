import os, sys

from termcolor import colored

class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout
        

def ask_for_num(msg, mx_num, min_num = 1):
    num = input(msg)
        
    if num.isdigit(): 
        num = int(num)
    else:
        num = min_num - 1
    
    while num > mx_num or num < min_num:
        print(colored("I beg your pardon?", 'red'))
        num = input(msg)
        
        if num.isdigit(): 
            num = int(num)
        else:
            num = min_num - 1
            
    return num