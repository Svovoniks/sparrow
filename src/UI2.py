from abc import ABC, abstractmethod
from os.path import isdir
from termcolor import colored
from src.ShowManager import ShowManager
from src.TorrentUtils import TorrentEngine
from src.Search import SearchEngine
from src.utils import ask_for_num, print_colored_list, ask_for_input, visual_wrapper
from src.Configuration import SCRIPT_LINE, TMP_FILE, TMP_FILE_STARTER, Configuration


class UIState(ABC):
    def __init__(self, args) -> None:
        self.startup_args = args
        self.cookie = None

    @property
    def config(self) -> Configuration:
        return self._config

    @property
    def show_manager(self) -> ShowManager:
        return self._show_manager

    @config.setter
    def config(self, config):
        self._config = config
        self._show_manager = ShowManager(config)

class Command(ABC):
    @abstractmethod
    def execute(self, state, cookie=None) -> 'Command | None':
        pass

class ExitCommand(Command):
    def execute(self, state, cookie=None) -> 'Command | None':
        print(colored("*** Exiting ***\n", "green"))
        return None

class UpdateCommand(Command):

    @visual_wrapper
    def execute(self, state, cookie=None) -> 'Command | None':
        updates, new_config = state.show_manager.check_for_updates()

        if len(updates) == 0:
            print(colored("\nEverything seems to be up to date", "green"))
            return MainScreenCommand()

        torrent_engine = TorrentEngine(
            state.config[SCRIPT_LINE],
        )

        print('Staging updates')
        for i in updates:
            torrent_engine.add_download(i)

        print('Starting downloading')
        torrent_engine.download()
        print(colored('\nAll done', "green"))

        print("\nAre we good? [y/n]")
        print(colored("ProTip: if some updates failed to start or you accidentally canceled them,\
            \nyou can skip the config update and try again (\"n\" to do this)", "cyan"))

        ans = ask_for_input("y (yes)")
        if not(len(ans) > 0 and ans[0] == "n"):
            state.config = new_config
            state.config.update_config()

        return MainScreenCommand()

class UpdateSilentCommand(Command):
    @visual_wrapper
    def execute(self, state, cookie=None) -> 'Command | None':
        UpdateCommand().execute(state)
        return None

class AddCommand(Command):

    @visual_wrapper
    def execute(self, state, cookie=None) -> 'Command | None':
        if cookie is None:
            print('Enter name of the show you want to add')
            show_name = ask_for_input('get confused')
        else:
            print(f'''\n{colored('Got cookie: "', "green")}{colored(cookie, "white")}{colored('"', "green")}\n''')
            show_name = cookie

        if show_name == '':
            print('Name is empty\nDo you want to try again [y/n]')
            if ask_for_input('n (main screen)') == 'y':
                return AddCommand()
            return MainScreenCommand()

        engine = SearchEngine()

        show = engine.find_show(show_name)

        if show == None:
            print(colored("Search didn't return any results", 'red'))
            return MainScreenCommand()

        if show in state.config.show_list:
            print(colored('This show was already in you list', 'red'))
            return MainScreenCommand()

        state.config.add_show(show)
        state.config.update_config()

        print(colored(f'Added: "{show.title}"', 'green'))

        return MainScreenCommand()

class ShowShowListCommand(Command):

    def execute(self, state, cookie=None) -> 'Command | None':
        shows = [("[Show name]", "[Source]")]
        for show in state.config.show_list:
            shows.append((show.title, show.parser_name))

        print_colored_list(shows, first_heading=True)
        return None

class RemoveCommand(Command):

    @visual_wrapper
    def execute(self, state, cookie=None) -> 'Command | None':
        show_titles = {show.title: idx for idx, show in enumerate(state.config.show_list)}
        if cookie in show_titles:
            print(f'''\n{colored('Got cookie: "', "green")}{colored(cookie, "white")}{colored('"', "green")}\n''')
            to_delete = [show_titles[cookie]]
        else:
            if cookie:
                print(f'''\n{colored('Discarded cookie: "', "red")}{colored(cookie, "white")}{colored('"', "red")}\n''')

            ShowShowListCommand().execute(state)
            to_delete = list(set(filter(lambda a: len(a) > 0, ask_for_input("back to main menu").replace(" ", ",").split(","))))
            
            for i in range(len(to_delete)):
                try:
                    to_delete[i] = int(to_delete[i])-1
                except Exception as e:
                    print(colored(f'Error: failed to parse "{to_delete[i]}" as number', 'red'))
                    return MainScreenCommand()
                
                if to_delete[i] < 0 or to_delete[i] >= len(state.config.show_list):
                    print(colored(f'Error: "{to_delete[i]+1}" is not a valid show number', 'red'))
                    return MainScreenCommand()

        # This is horrible, but whatever it's python
        to_delete = list(map(lambda a: state.config.show_list[a], to_delete))
        for i in to_delete:
            print(colored(f'Deleted: "{i.title}"', 'red'))
            state.config.remove_show(i)
            
        state.config.update_config()

        return MainScreenCommand()


class ListCommand(Command):

    @visual_wrapper
    def execute(self, state, cookie=None) -> 'Command | None':
        print('Your show list:')
        ShowShowListCommand().execute(state)

        print("Did you get a good look?\nI'm waiting for you to hit that Enter")
        ask_for_input('main screen')

        return MainScreenCommand()

class GetConfigCommand(Command):
    def execute(self, state, cookie=None) -> 'Command | None':
        print("I couldn't find a config file")
        print("So let's get you started")
        print("Where would you like me to put new episodes?")

        download_dir = ask_for_input('ask again')

        while not isdir(download_dir):
            print(colored("Error: not a real folder", 'red'))
            print("Try again")

            download_dir = ask_for_input('ask again')

        config = Configuration.create_config(download_dir)

        print(colored("You are all set", 'green'))
        print(colored("Please don't remove last episode of each show", 'green'))
        print(colored("So i know what you've watched already", 'green'))
        state.config = config

        return None

class MainScreenCommand(Command):

    @visual_wrapper
    def execute(self, state, cookie=None) -> 'Command | None':
        screen_list = [
            ('[Action]', '[Cookie support]'),
            ('update', 'update all shows', UpdateCommand, "False"),
            ('add', 'add show', AddCommand, "True"),
            ('remove', 'remove show', RemoveCommand, "True"),
            ('list', 'list tracked shows', ListCommand, "False"),
            ('exit', '"" | exit', ExitCommand, "False"),
        ]

        screens_map = {'': ExitCommand}

        for idx, el_tp in enumerate(screen_list[1:]):
            screens_map[str(idx+1)] = el_tp[2]
            screens_map[el_tp[0]] = el_tp[2]

        print('You can:')

        print_colored_list(screen_list, mapper=lambda a: (a[1], a[3]), first_heading=True)
        print("What do you want?\nEnter number or the first word of the action you want to perform")
        print(colored("ProTip: if action supports cookies you can pass arguments to the next step,"
            "\nif you know what comes next that is", "cyan"))

        while True:
            next_screen = ask_for_input('ask again')
            cookie = None
            if " " in next_screen:
                next_screen, cookie = next_screen.split(" ", 1)

            if next_screen in screens_map:
                break

            print(colored("I beg your pardon??", 'red'))

        state.cookie = cookie
        return screens_map[next_screen]()

class StartUI(Command):
    def execute(self, state, cookie=None) -> 'Command | None':
        config = Configuration.try_parse_config()

        if config == None:
            GetConfigCommand().execute(state)
        else:
            state.config = config

        quick_actions = {
            'update': UpdateSilentCommand,
        }

        if len(state.startup_args) == 1:
            return quick_actions.get(state.startup_args[0], MainScreenCommand)()

        return MainScreenCommand()

def run_ui(args):
    state = UIState(args)
    command = StartUI()
    cookie = state.cookie

    while command is not None:
        command = command.execute(state, cookie=cookie)
        cookie = state.cookie
        state.cookie = None


