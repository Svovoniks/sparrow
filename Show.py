from ConfigManager import Configuration


class ShowManager:
    def __init__(self, config: Configuration) -> None:
        self.config = config
        
    def check_for_updates(self):
        for i in self.config.title_list:
            pass



class Show:
    def __init__(self, exact_title, parser_name) -> None:
        self.exact_title = exact_title
        self.parser_name = parser_name
        
    def check_for_update(self):
        pass
        
        
    def to_json(self):
        return {
            "title": self.exact_title,
            "parser": self.parser_name
        }
        
    @staticmethod
    def from_json(json_obj):
        return Show(json_obj["title"], json_obj["parser"])
