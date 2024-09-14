import configparser
import os
import unittest

import pyanty as dolphin
from pyanty import DolphinAPI

config_path = os.path.join(os.path.dirname(__file__), "config.ini")
config = configparser.ConfigParser()
config.read(config_path)

from main import InstagramBot

DOLPHIN_TOKEN = config.get("DEFAULT", "DOLPHIN_TOKEN")
OPENAI = config.get("DEFAULT", "OPENAI")
api = DolphinAPI(api_key=DOLPHIN_TOKEN)


class InstagramBotFunctionalTest(unittest.TestCase):

    def setUp(self):
        # Start Playwright
        self.profile_id = "456052958"

        self.bot = InstagramBot()

        # Instagram credentials (set up in your environment variables for security)
        self.instagram_username = os.getenv("INSTAGRAM_USERNAME")
        # self.instagram_password = os.getenv("INSTAGRAM_PASSWORD")

    def test_send_message(self):
        # Login first (reuse the login test code)
        result = self.bot.check_inbox_and_reply()
        self.assertTrue(result)
    def tearDown(self):
        # Close the browser after each test
        dolphin.close_profile(self.profile_id)
        # Stop Playwright


if __name__ == '__main__':
    unittest.main()
