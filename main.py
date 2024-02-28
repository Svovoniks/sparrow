from src.UI import UI
from colorama import just_fix_windows_console
just_fix_windows_console()

# if __name__ == "__main__":
#     UI.start()


from src.Parsers.TokyoToshokanParser import TokyoToshokanParser

parser = TokyoToshokanParser()

arr = parser.get_all_shows('one piece')

print(len(arr))

for i in arr:
    print(i[0])
