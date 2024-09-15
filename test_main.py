import configparser
import os
import unittest

import pyanty as dolphin
from pyanty import DolphinAPI

config_path = os.path.join(os.path.dirname(__file__), "config.ini")
config = configparser.ConfigParser()
config.read(config_path)

from main import check_inbox_and_reply

DOLPHIN_TOKEN = config.get("DEFAULT", "DOLPHIN_TOKEN")
api = DolphinAPI(api_key=DOLPHIN_TOKEN)


class InstagramBotFunctionalTest(unittest.TestCase):

    def setUp(self):
        # Start Playwright
        self.profile_id = "456052958"

    def test_send_message(self):
        # Login first (reuse the login test code)
        result = check_inbox_and_reply()
        self.assertTrue(result)
    def tearDown(self):
        # Close the browser after each test
        dolphin.close_profile(self.profile_id)
        # Stop Playwright


if __name__ == '__main__':
    unittest.main()
