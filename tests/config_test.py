import unittest
import os
import tempfile

from src.Show import Show
from src.Configuration import Configuration, DOWNLOAD_DIR, SHOW_LIST


class ConfigTestCase(unittest.TestCase):

    # run every test in a temp dir so we never touch a real config file
    def setUp(self):
        self._old_cwd = os.getcwd()
        self._tmp_dir = tempfile.TemporaryDirectory()
        os.chdir(self._tmp_dir.name)

    def tearDown(self):
        os.chdir(self._old_cwd)
        self._tmp_dir.cleanup()

    def test_config_file_opearations(self):
        sample = Configuration.get_sample_config()
        config = Configuration.create_config(sample[DOWNLOAD_DIR])

        res_config = Configuration.try_get_config_json()

        self.assertEqual(config.config_json, res_config)

    def test_add_show(self):
        config = Configuration(Configuration.get_sample_config())

        show = Show('show', 'parser', 'filter', 'link', None)

        self.assertNotIn(show, config.show_list)
        config.add_show(show)
        self.assertIn(show, config.show_list)

    def test_remove_show(self):
        config = Configuration(Configuration.get_sample_config())

        show = Show('show', 'parser', 'filter', 'link', None)

        config.add_show(show)
        self.assertIn(show, config.show_list)
        config.remove_show(show)
        self.assertNotIn(show, config.show_list)
        self.assertEqual(config.config_json[SHOW_LIST], [])

    def test_check_config_json(self):
        invalid = {
            'not enough': 'data'
        }

        self.assertFalse(Configuration.check_config_json(invalid))
        self.assertTrue(Configuration.check_config_json(Configuration.get_sample_config()))

if __name__ == '__main__':
    unittest.main()
