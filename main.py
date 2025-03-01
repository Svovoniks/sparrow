from src.UI import UI
from colorama import just_fix_windows_console
import sys

if __name__ == "__main__":
    just_fix_windows_console()

    args = []
    if len(sys.argv) > 1:
        args = sys.argv[1:]

    UI.start(args)

