import configparser
import os
import unittest

import pyanty as dolphin
from pyanty import DolphinAPI

config_path = os.path.join(os.path.dirname(__file__), "config.ini")
config = configparser.ConfigParser()
config.read(config_path)

from main import check_inbox_and_reply, get_last_hundred_messages

DOLPHIN_TOKEN = config.get("DEFAULT", "DOLPHIN_TOKEN")
api = DolphinAPI(api_key=DOLPHIN_TOKEN)


class InstagramBotFunctionalTest(unittest.TestCase):

    def setUp(self):
        # Start Playwright
        self.profile_id = ""

    def test_send_message(self):
        # Login first (reuse the login test code)
        result = check_inbox_and_reply()
        self.assertTrue(result)

    def test_get_last_hundred_messages(self):
        result = get_last_hundred_messages(page)
        self.assertTrue(len(result) > 0)
    def tearDown(self):
        # Close the browser after each test
        dolphin.close_profile(self.profile_id)
        # Stop Playwright


if __name__ == '__main__':
    unittest.main()
