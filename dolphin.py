import configparser
import json
import os
import platform
import random
import string
import subprocess
import time

import requests
from playwright.sync_api import sync_playwright

# Playwright code that causes a TikTok captcha...


BASE_URL = f"https://anty-api.com"

config_path = os.path.join(os.path.dirname(__file__), "config.ini")
config = configparser.ConfigParser()
config.read(config_path)
DOLPHIN_EMAIL = config.get("DEFAULT", "DOLPHIN_EMAIL")
DOLPHIN_PASS = config.get("DEFAULT", "DOLPHIN_PASS")
DOLPHIN_TOKEN = config.get("DEFAULT", "DOLPHIN_TOKEN")


def login_dolphin():
    url = f"{BASE_URL}/auth/login"

    payload = {'username': DOLPHIN_EMAIL, 'password': DOLPHIN_PASS}
    headers = {}
    for i in range(0, 15):
        try:
            return requests.post(url, headers=headers, data=payload).json()["DOLPHIN_TOKEN"]

        except:
            time.sleep(2)
            continue


# print(DOLPHIN_TOKEN)

def stop_browsers(profile_ids):
    for i in range(0, 15):

        try:

            return requests.get(f"http://localhost:3001/v1.0/browser_profiles/{profile_ids}/stop").json

        except:
            continue



def launch_browser(id):
    headers = {'Authorization': f'Bearer {DOLPHIN_TOKEN}', 'Content-Type': 'application/json'}

    for i in range(0, 15):
        try:
            response = requests.get(f"http://localhost:3001/v1.0/browser_profiles/{id}/start?automation=1",
                                    headers=headers)
            print(response.text)
            endpoint = response.json()["automation"]["wsEndpoint"]

            port = response.json()["automation"]["port"]

            return endpoint, port

        except:
            continue


def launch_browser_playwright_dolphin(port, endpoint):
    p = sync_playwright().start()

    browser = p.chromium.connect_over_cdp(f"ws://127.0.0.1:{port}{endpoint}")
    default_context = browser.contexts[0]
    page = default_context.pages[0]

    return page


def get_page_content_with_retry(page, max_retries=5, delay=1):
    for attempt in range(max_retries):
        try:
            content = page.content()
            return content
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(delay)
    raise Exception("Max retries exceeded for getting page content")




