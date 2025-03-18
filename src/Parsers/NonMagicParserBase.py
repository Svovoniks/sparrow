import re
from termcolor import colored
from src.Parsers.ParserBase import ParserBase
from src.Show import Show
from src.utils import ask_for_input, ask_for_num, print_colored_list
import pyperclip as pc

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

    def process_user_filter(self, _filter):
        real_rgx = r'.*'
        user_rgx = r'<<[^(>>)]*>>'

        fl = re.escape(_filter)
        fl = re.sub(user_rgx, real_rgx, fl)

        return fl


    def apply_filter(self, real_filter, episodes):
        return list(filter(lambda a: re.fullmatch(real_filter, a[0]) != None, episodes))

    def get_filter(self, title, episodes):
        print('This website is an aggregator of shows from multiple sources')
        print("And each source has it's own naming scheme")
        print("To solve this problem we would need an AI, or a separate parser for each source")
        print("Spoiler: This program is none of those things")
        print("So we are going to have to outsource this task to some external AI, an AGI perhaps")
        print("As you may have guessed, we are going to use you")
        print()
        print("Here is what you have to do:")
        print(f'1. Look at this filename "{colored(title, "green")}"')
        print(f'2. Encase parts of it that can change from one episode to the next like this: <<{colored("variable", "green")}>>')
        print()
        print(f'''For example if filename is {colored('"[SubsPlease] Metallic Rouge - 08 (1080p) [19D9D43F].mkv"', 'yellow')} than''')
        print(f'''You should change it to {colored('"[SubsPlease] Metallic Rouge - <<08>> (1080p) <<[19D9D43F]>>.mkv"', 'yellow')}''')
        print('''And don't type ""''')

        print()
        print(colored("ProTip: filname you selected is in you clipboard", 'cyan'))


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
