REQUIRED_SHOW_FIELDS = ['show_title', 'parser', 'filter', 'link', 'last_episode']

class Show:
    def __init__(self, exact_title: str, parser_name: str, filter: str, link: str, last_episode: str) -> None:
        self.title = exact_title
        self.link = link
        self.parser_name = parser_name
        self.filter = filter
        self.last_episode = last_episode


    def to_json(self):
        """
        returns dict object that represents show
        """
        return {
            "show_title": self.title,
            "parser": self.parser_name,
            "filter": self.filter,
            "link": self.link,
            "last_episode": self.last_episode,
        }


    @staticmethod
    def check_json(json_obj) -> bool:
        """
        checks if json_obj contains all required information
        """
        return all([i in json_obj for i in REQUIRED_SHOW_FIELDS])


    @staticmethod
    def from_json(json_obj):
        """
        returns Show object represented by json_obj or None if json is not valid
        """
        if not Show.check_json(json_obj):
            json_cp = json_obj.copy()

            missing = []

            for i in REQUIRED_SHOW_FIELDS:
                if i not in json_cp:
                    missing.append(i)

            print(f'Error: Found entry with missing {", ".join(missing)}')
            print(f'Please fix it or remove it from the config file')
            return None

        return Show(json_obj["show_title"], json_obj["parser"], json_obj["filter"], json_obj["link"], json_obj["last_episode"])

    def __eq__(self, __value) -> bool:
        if __value == None:
            return False

        return all([
            self.title == __value.title,
            self.parser_name == __value.parser_name,
            self.link == __value.link,
            self.filter == __value.filter,
        ])

    def __repr__(self) -> str:

        return str((
            self.title,
            self.last_episode,
            self.parser_name,
            self.link,
            self.filter,
        ))
