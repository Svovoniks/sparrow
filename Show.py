from collections import defaultdict
from typing import List, Optional, Self
from Configuration import CONFIG_FILE, Configuration
from Parsers.ParserFactory import PARSER_MAP, get_parser_by_name


REQUIRED_SHOW_FIELDS = ['show_title', 'parser', 'key']

class Show:
    def __init__(self, exact_title, parser_name, key) -> None:
        self.title = exact_title
        self.parser_name = parser_name
        self.key = key
        
    def check_for_updates(self, download_folder_contents) -> list[str]:
        """
        returns list of magnet links for the new episodes of the show
        """ 
        return get_parser_by_name(self.parser_name).check_show(self, download_folder_contents)
        
        
    def to_json(self):
        """
        returns dict object that represents show
        """
        return {
            "show_title": self.title,
            "parser": self.parser_name,
            "key": self.key,
        }
        
        
    def check_json(json_obj) -> bool:
        """
        checks if json_obj contains all required information
        """
        return all([i in json_obj for i in REQUIRED_SHOW_FIELDS])
    
    
    @staticmethod
    def from_json(json_obj: dict) -> Optional[Self]:
        """
        returns Show object represented by json_obj or None if json is not valid
        """
        if not Show.check_json(json_obj):
            json_cp = json_obj.copy()
            
            missing = []
            
            for i in REQUIRED_SHOW_FIELDS:
                if i not in json_cp:
                    missing.append(i)
                    
            print(f'Error: Found entry with missing {', '.join(missing)}')
            print(f'Please fix it or remove it from the "{CONFIG_FILE}" file')
            return None
        
        return Show(json_obj["show_title"], json_obj["parser"], json_obj["key"])

