import configparser
import os
import unittest

import pyanty as dolphin
from pyanty import DolphinAPI

from main import InstagramBot

config_path = os.path.join(os.path.dirname(__file__), "config.ini")
config = configparser.ConfigParser()
config.read(config_path)


DOLPHIN_TOKEN = config.get("DEFAULT", "DOLPHIN_TOKEN")
api = DolphinAPI(api_key=DOLPHIN_TOKEN)


class InstagramBotFunctionalTest(unittest.TestCase):

    def setUp(self):
        # Start Playwright
        self.profile_id = "459894232"
        self.bot = InstagramBot()
        self.bot.start_playwright()
    def test_send_message(self):
        # Login first (reuse the login test code)
        result = self.bot.check_inbox_and_reply()
        self.assertTrue(result)

    def test_get_last_hundred_messages(self):
        result = self.bot.get_last_hundred_messages()
        print(result)
        self.assertTrue(len(result) > 0)
    def tearDown(self):
        # Close the browser after each test
        dolphin.close_profile(self.profile_id)
        # Stop Playwright


if __name__ == '__main__':
    unittest.main()
