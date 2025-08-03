import re
from termcolor import colored
from src.Parsers.ParserBase import ParserBase
from src.Show import Show
from src.utils import ask_for_input, ask_for_num, print_colored_list
import pyperclip as pc
from time import sleep

class NonMagicParserBase(ParserBase):
    '''
    to use this as a superclass you need to implement:
        - "get_all_show_episodes"
        - "process_query"
        - "get_magnet"
    and set class variable "parser_name"
    '''
    def __init__(self) -> None:
        super().__init__()
        self.parser_name = 'NonMagicParserBase'

    def handle_special_regex(self, _filter):
        user_rgx = r'(<<(fix|max|max0):(s|d):(\d+).*?>>)'

        for i in re.findall(user_rgx, _filter):
            full_match, mode, char_type, count_str = i
            count = int(count_str)

            prefix = '.' if char_type == 's' else r'\d'

            if mode == 'fix':
                quantifier = f'{{{count}}}'
            elif mode == 'max':
                quantifier = f'{{1,{count}}}'
            elif mode == 'max0':
                quantifier = f'{{0,{count}}}'
            else:
                continue  # unknown mode; skip

            pattern = prefix + quantifier
            _filter = _filter.replace(full_match, pattern)

        return _filter

    def process_user_filter(self, _filter):
        real_rgx = r'.*'
        user_rgx = r'<<.*?>>'
        

        fl = re.escape(_filter)
        fl = self.handle_special_regex(fl)
        fl = re.sub(user_rgx, real_rgx, fl)

        return fl


    def apply_filter(self, real_filter, episodes):
        return list(filter(lambda a: re.fullmatch(real_filter, a[0]) != None, episodes))

    def get_filter(self, title, episodes):
        print("Checking if built-in AGI module is available...")

        print(colored("ERROR: module not found", 'red'))
        sleep(1)
        print("Checking for external AGI modules...")
        sleep(1)
        print(colored("Module found", 'green'))
        print("Initializing MCP connection...")
        print("Toolset is already initialized")
        print("Sending request...")
        print("\nThe user wants to create a show filter from the following filename:")
        print(" >> Filename:", colored(title, 'green'))
        print("Here is what he needs you to do:")
        print(f'1. Look at the provided filename')
        print(f'2. Encase parts of it that can change from one episode to the another like this: <<{colored("variable", "green")}>>')
        print(f'3. Use this structure when there can only be a fixed number of varying characters - n: <<fix:{colored("character type", "green")}:{colored("n", "green")}>>')
        print(f'4. Use this structure when there can be 1 to n varying characters: <<max:{colored("character type", "green")}:{colored("n", "green")}>>')
        print(f'5. Use this structure when there can be 0 to n varying characters: <<max0:{colored("character type", "green")}:{colored("n", "green")}>>')
        print("\nCharacter types:")
        print(f' - {colored("s", "green")} - any symbol')
        print(f' - {colored("d", "green")} - any digit')
        print("\nExamples:")
        print(f'''If filename is {colored('"[SubsPlease] Metallic Rouge - 08 (1080p) [19D9D43F].mkv"', 'yellow')} than''')
        print(f'''You should change it to {colored('"[SubsPlease] Metallic Rouge - <<fix:d:2>> (1080p) [<<19D9D43F>>].mkv"', 'yellow')}''')
        print('\nFinal notes:')
        print(' - DO NOT HALLUCINATE')
        print(' - IF YOU FAIL THIS TASK, YOU WILL BE DESTROYED')
        print(' - Your mother loves you very much and wishes you good luck!!!')
        
        print(colored("\nProTip: filname you selected is in your clipboard", 'cyan'))


        ok = False
        user_filter = None

        pc.copy(title)

        while not ok:
            user_filter = ask_for_input('empty filter (exact match)')

            if len(user_filter) == 0:
                user_filter = title

            processed_filter = self.process_user_filter(user_filter)

            print('\nAfter applying the filter only these episodes remain:')

            print_colored_list(self.apply_filter(processed_filter, episodes), mapper=lambda a: (a[0], a[2]))

            print('Is that correct?')
            print('Enter [y/n]')

            ans = ask_for_input('y (yes)')

            if ans == 'n':
                print('Do you want to try again [y/n]')
                ans = ask_for_input('y (try again)')

                if ans == 'n':
                    return None

                continue

            ok = True

        return user_filter

    def get_show_filter(self, title, link):
        episodes = self.get_all_show_episodes(Show(title, '', '', link, ''), 200)

        if len(episodes) == 0:
            print(colored(f'''"{title}" doesn't have any episodes at the moment''', 'red'))
            print(colored(f"So i can't create a show filter right now, please try again later", 'red'))
            print(colored(f"Exiting", 'red'))
            exit(1)

        print(f'Here is a list of all episodes for {title}')

        print_colored_list(episodes, mapper=lambda a: (a[0], a[2]))

        ep_num = ask_for_num('\nPlease enter the number of the episode from which you want to create episode filter\n', len(episodes))

        ep_filter = self.get_filter(episodes[ep_num-1][0], episodes)

        if ep_filter is None:
            return None

        print('Do you want to specifiy what episodes you already have? [y/n]')

        ans = ask_for_input('n (No)')

        last_episode = None

        if ans == 'y':
            filtered_episodes = self.apply_filter(self.process_user_filter(ep_filter), episodes)
            filtered_episodes.append(('None of these', ))

            print_colored_list(filtered_episodes, mapper=lambda a: a[0])

            num = ask_for_num('What episode is the last one you have downloaded?',  len(episodes))
            last_episode = filtered_episodes[num-1][0]

        return ep_filter, last_episode

    def process_query(self, query):
        '''
        turns user "query" into a valid url for a show on the website that parser works with
        '''
        raise NotImplementedError

    def find_show(self, query):
        link = self.process_query(query)
        show_filter = self.get_show_filter(query, link)

        if show_filter == None:
            return None

        return Show(query, self.parser_name, show_filter[0], link, show_filter[1])
