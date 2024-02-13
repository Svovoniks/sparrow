import requests


class ParserInterface:
    def __init__(self, download_folder_contents) -> None:
        self.parser_name = 'Default'
        self.download_folder_contents = download_folder_contents

    def check_title(self, title):
        pass
    
    def load_page(self, url):
        resp = requests.get(url)
        
        if resp.status_code != 200:
            print(f"Couldn't load {self.parser_name}")
            return None
        
        return resp

