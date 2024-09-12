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
            response = requests.get(f"http://localhost:3001/v1.0/browser_profiles/{id}/start?automation=1", headers=headers)

            # Check if the response status code is OK (200)
            if response.status_code != 200:
                print(f"Failed to get response. Status code: {response.status_code}")
                continue

            print(response.text)
            response_json = response.json()

            # Ensure the necessary fields are present
            if "automation" not in response_json or "wsEndpoint" not in response_json["automation"] or "port" not in response_json["automation"]:
                print(f"Missing 'automation' key or 'wsEndpoint' or 'port' in the response: {response_json}")
                continue

            endpoint = response_json["automation"]["wsEndpoint"]
            port = response_json["automation"]["port"]

            return endpoint, port

        except Exception as e:
            print(f"Error occurred: {str(e)}")
            continue

    return None, None  # In case all 15 retries fail


def launch_browser_playwright_dolphin(port, endpoint):
    try:
        p = sync_playwright().start()

        # Create the WebSocket URL from the provided port and endpoint
        ws_url = f"ws://127.0.0.1:{port}{endpoint}"
       # print(f"Connecting to WebSocket: {ws_url}")

        # Connect using Playwright
        browser = p.chromium.connect_over_cdp(f"http://localhost:{port}")

        default_context = browser.contexts[0]
        page = default_context.pages[0]

        print("Successfully connected to the browser via CDP.")
        return page
    except Exception as e:
        print(f"Error while connecting to WebSocket: {str(e)}")
        return None

def get_page_content_with_retry(page, max_retries=5, delay=1):
    for attempt in range(max_retries):
        try:
            content = page.content()
            return content
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(delay)
    raise Exception("Max retries exceeded for getting page content")




