from ParserBase import ParserBase
import re

class EZTVParser(ParserBase):
    def __init__(self) -> None:
        super().__init__()
        self.main_url = 'https://eztvx.to/'
        self.all_shows_url = 'https://eztvx.to/showlist/'
        
    def check_show(self, show, download_folder_contents: str) -> list[str]:
        return []
    
    def get_all_shows(self) -> list[list[str]]:
        """
        Returns:
            list[list[str]]: list of all shows on the site available on the site
            if the form of [[title1, link_to_the_show_page], [title2, link_to_the_show_page]]
        """
        page = self.load_page(self.all_shows_url)
        pattern = r'''<td class="forum_thread_post"><a href="([^"]+)" class="thread_link">([^"]+)</a></td>'''
        
        if page == None:
            return None
        
        return [(i[1], self.main_url + i[0]) for i in re.findall(pattern, page.text)]
    
    
    def get_all_show_episodes(self, page):
        pattern = r'''<a href="/([^"]+)" title="([^"]+)" alt="([^"]+)" class="epinfo">([^"]+)</a></td><td align="center" class="forum_thread_post">([^"]+)</td>'''
        
        
    
    def get_show_filter(self, title, link):
        page = self.load_page(link)
        
        
        return ''
    
    
print(EZTVParser().get_all_shows())

