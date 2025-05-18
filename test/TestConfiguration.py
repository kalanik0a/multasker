import json

from multasker.util import Configuration
from multasker.test import Test

class TestConfiguration(Test):
    def __init__(self, method):
        super(TestConfiguration, self).__init__(method)

    def test_01_LoadConfiguration(self):
        config = Configuration(config_path='testdata/config.yaml')
        config_data = config.get_config()
        if config_data is not None and config_data['configuration']['api_key_path']:
            config.config['configuration']['api_key'] = config.open_file_path(config_data['configuration']['api_key_path'])
        print(json.dumps(config_data, indent=4))
        self.assertIsNot(config_data, None)
        self.assertEqual(config.config['configuration']['api_key'], 'abcdefghijklmnop0123456789')