import unittest

from src.Show import Show

json_show_obj = {
            "show_title": 'title',
            "parser": 'parser',
            "filter": 'show filter',
            "link": 'https://show.com',
        }

json_show_obj_invalid = {
            "show_title": 'title',
            "parser": 'parser',
            "filter": 'show filter',
        }


show_obj = Show('title', 'parser', 'show filter', 'https://show.com')

class ShowTestCase(unittest.TestCase):
    
    def test_to_json(self):
        self.assertEqual(show_obj.to_json(), json_show_obj)
    
    def test_from_json(self):
        self.assertEqual(Show.from_json(json_show_obj), show_obj)
        self.assertEqual(Show.from_json(json_show_obj_invalid), None)

if __name__ == '__main__':
    unittest.main()
    