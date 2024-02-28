import os, sys, math

from termcolor import colored


class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout
        

def ask_for_num(msg, mx_num, min_num = 1):
    print(msg)
    num_str = ask_for_input('ask again')
    
    num = num_str
    
    if num.isdigit(): 
        num = int(num)
    else:
        num = min_num - 1
    
    while num > mx_num or num < min_num:
        if num_str == 'exit':
            exit(0)
            
        print(colored("I beg your pardon?", 'red'))
        print(colored('ProTip: If you are being repeatedly asked to do something against your will just quietly type "exit"', 'blue'))
        
        num_str = ask_for_input('ask again')
        num = num_str
        
        if num.isdigit(): 
            num = int(num)
        else:
            num = min_num - 1
            
    return num

def verify_num_input(num: str, mx_num, min_num = 1):
    return num.isdigit() and int(num) <= mx_num and int(num) >= min_num

def print_colored_list(_list: list[str], color = 'cyan', line_color = 'yellow', mapper = lambda a: a):
    print(colored("_______________________", line_color))
    
    idx_space = 1 + int(math.log(len(_list), 10))
    
    for idx, el in enumerate(_list):
        print(colored(('{0:' + str(idx_space) + 'd}. ').format(idx+1) +  f'{mapper(el)}', color))
    
    print(colored("_______________________", line_color))
    
def ask_for_input(default_action: str, prompt_color='green'):
    print()
    return str(input(colored(f'[default: {default_action}] > ', prompt_color))).strip()