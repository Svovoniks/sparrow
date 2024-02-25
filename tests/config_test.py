import unittest

from src.Show import Show
from src.Configuration import Configuration, CONFIG_FILE, SAMPLE_CONFIG, DOWNLOAD_DIR
from os import remove


class ConfigTestCase(unittest.TestCase):
    
    def test_config_file_opearations(self):
        config = Configuration.create_config(SAMPLE_CONFIG[DOWNLOAD_DIR])
        
        res_config = Configuration.try_get_config_json()
        
        self.assertEqual(config.config_json, res_config)
        remove(CONFIG_FILE)
    
    def test_add_show(self):
        config = Configuration(SAMPLE_CONFIG)
        
        show = Show('show', 'parser', 'filter', 'link')
        
        self.assertNotIn(show, config.show_list)
        config.add_show(show)
        self.assertIn(show, config.show_list)    
    
    def test_check_config_json(self):
        invalid = {
            'not enough': 'data'
        }
        
        self.assertFalse(Configuration.check_config_json(invalid))
        self.assertTrue(Configuration.check_config_json(SAMPLE_CONFIG))

if __name__ == '__main__':
    unittest.main()
    