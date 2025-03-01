import os, sys, math

from termcolor import colored

def visual_wrapper(func):
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        print()
        return res
    return wrapper

class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stderr.close()
        sys.stdout = self._original_stdout
        sys.stderr = self._original_stderr


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
        print(colored('ProTip: If you are being repeatedly asked to do something against your will just quietly type "exit"', 'cyan'))

        num_str = ask_for_input('ask again')
        num = num_str

        if num.isdigit():
            num = int(num)
        else:
            num = min_num - 1

    return num

def verify_num_input(num: str, mx_num, min_num = 1):
    return num.isdigit() and int(num) <= mx_num and int(num) >= min_num



def map_to_columns(_list):
    if len(_list) == 0:
        return _list

    res_arr = None

    if not (type(_list[0]) == type(list()) or type(_list[0]) == type(tuple())):
        _list = list(map(lambda a: [a], _list))

    res_arr = [None]*len(_list)
    mx_arr = [0]*len(_list[0])

    for i in range(len(_list)):
        for j in range(len(_list[i])):
            mx_arr[j] = max(mx_arr[j],  len(_list[i][j]))

    for i in range(len(_list)):
        res_arr[i] = []
        for j in range(len(_list[i])):
            res_arr[i].append(('{0:' + str(mx_arr[j]) + '}').format(_list[i][j]))

    return res_arr

def print_colored_list(_list, color = 'cyan', line_color = 'yellow', mapper = lambda a: a, first_heading=False, col_sep='   '):
    print(colored("_______________________", line_color))

    column_list = []
    if first_heading:
        column_list.append(_list[0])

    column_list.extend(list(map(mapper, _list[int(first_heading):])))
    column_list = map_to_columns(column_list)

    idx_space = 1 + int(math.log(max(len(_list), 1), 10))

    if first_heading:
        print(colored(' '*idx_space + '  ' + col_sep.join(column_list[0]), 'yellow'))

    idx_space = 1 + int(math.log(max(len(_list), 1), 10))

    for idx, el in enumerate(column_list[int(first_heading):]):
        print(colored(('{0:' + str(idx_space) + 'd}. ').format(idx+1) +  col_sep.join(el), color))

    print(colored("_______________________", line_color))

def ask_for_input(default_action: str, prompt_color='green'):
    print()
    return str(input(colored(f'[default: {default_action}] > ', prompt_color))).strip()
