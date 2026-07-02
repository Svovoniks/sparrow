from colorama import just_fix_windows_console
import sys

if __name__ == "__main__":
    just_fix_windows_console()

    args = []
    if len(sys.argv) > 1:
        args = sys.argv[1:]

    if len(args) > 0 and args[0] == 'gui':
        from src.GUI import run_gui
        run_gui()
    else:
        from src.UI2 import run_ui
        run_ui(args)

