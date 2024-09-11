import configparser
import json
import os
import platform
import random
import string
import subprocess
import time

import requests
from faker import Faker
from playwright.sync_api import sync_playwright
from twocaptcha import TwoCaptcha
from tiktok_captcha_solver import PlaywrightSolver
from playwright.sync_api import Page, sync_playwright


# Playwright code that causes a TikTok captcha...


BASE_URL = f"https://anty-api.com"

config_path = os.path.join(os.path.dirname(__file__), "..", "config.ini")
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

def generate_random_string(length=10):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))


def create_random_profile():
    url = "https://dolphin-anty-api.com/browser_profiles"
    headers = {
        "Authorization": f"Bearer {DOLPHIN_TOKEN}",
        "Content-Type": "application/json"
    }

    random_name = generate_random_string(10)
    profile_data = {
        "name": random_name,
        "platform": "windows",
        "browserType": "anty",
        "useragent": {
            "mode": "manual",
            "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        },
        "webrtc": {
            "mode": "off",
            "ipAddress": None
        },
        "canvas": {
            "mode": "real"
        },
        "webgl": {
            "mode": "real"
        },
        "webglInfo": {
            "mode": "manual",
            "vendor": "Google Inc. (AMD)",
            "renderer": "ANGLE (AMD, AMD Radeon(TM) Graphics Direct3D11 vs_5_0 ps_5_0, D3D11)"
        },
        "timezone": {
            "mode": "auto",
            "value": None
        },
        "locale": {
            "mode": "auto",
            "value": None
        },
        "cpu": {
            "mode": "manual",
            "value": 12
        },
        "memory": {
            "mode": "manual",
            "value": 8
        },
        "screen": {
            "mode": "real"
        }
    }

    response = requests.post(url, headers=headers, json=profile_data)

    if response.status_code == 200:
        profile_id = response.json().get('data', {}).get('id')
        profile_name = response.json().get('data', {}).get('name')
        print(profile_name)
        return profile_id
    else:
        print("Failed to create profile:", response.text)
        return None


def stop_browsers(profile_ids):
    for i in range(0, 15):

        try:

            return requests.get(f"http://localhost:3001/v1.0/browser_profiles/{profile_ids}/stop").json

        except:
            continue


def get_all_active_profiles():
    response = requests.get('https://dolphin-anty-api.com/browser_profiles',
                            headers={'Authorization': f'Bearer {DOLPHIN_TOKEN}'})
    profiles = response.json().get('data', [])
    active_profiles = [profile for profile in profiles if profile.get('running')]
    return active_profiles


def close_browser(profile_id):
    response = requests.post(f'https://dolphin-anty-api.com/browser_profiles/{profile_id}/stop',
                             headers={'Authorization': f'Bearer {DOLPHIN_TOKEN}'})
    if response.status_code == 200:
        print(f"Successfully closed browser for profile ID: {profile_id}")
    else:
        print(f"Failed to close browser for profile ID: {profile_id}")


def close_all_browsers():
    active_profiles = get_all_active_profiles()
    for profile in active_profiles:
        close_browser(profile['id'])


def get_all_profiles():
    url = f"{BASE_URL}/browser_profiles/"
    headers = {'Authorization': f'Bearer {DOLPHIN_TOKEN}', 'Content-Type': 'application/json'}
    payload = {}

    for i in range(0, 15):

        try:
            return requests.request("GET", url, headers=headers, data=payload).json()
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


def solve_recaptcha(current_url, captcha_key, sitekey):
    solver = TwoCaptcha(captcha_key)

    result = solver.recaptcha(sitekey=sitekey,
                              url=current_url)

    return result["code"]


def launch_browser_playwright_dolphin(port, endpoint):
    p = sync_playwright().start()

    browser = p.chromium.connect_over_cdp(f"ws://127.0.0.1:{port}{endpoint}")
    default_context = browser.contexts[0]
    page = default_context.pages[0]

    return page


def generate_random_name():
    fake = Faker()
    first_name = fake.first_name()
    surname = fake.last_name()
    return first_name, surname


def randomword(length):
    import random

    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def download_file_requests(link):
    s = requests.Session()

    r = s.get(link, timeout=30)

    f = open(f"{randomword}.jpeg", 'wb')
    print("Downloading.....")
    for chunk in r.iter_content(chunk_size=255):
        if chunk:  # filter out keep-alive new chunks
            f.write(chunk)
    f.close()


def check_if_file_exists(path):
    return os.path.isfile(path)


def human_type(element, text):
    for char in text:
        time.sleep(random.uniform(0.1, 0.5))  # fixed a . instead of a
        element.type(char)


# Function to delete all existing profiles
def delete_all_profiles():
    url = f"{BASE_URL}/browser_profiles?limit=50"
    headers = {
        "Authorization": f"Bearer {DOLPHIN_TOKEN}",
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        profiles = response.json().get('data', [])
        profile_ids = [profile['id'] for profile in profiles]
        if profile_ids:
            delete_url = f"{BASE_URL}/browser_profiles?forceDelete=1"
            delete_response = requests.delete(delete_url, headers=headers, json={"ids": profile_ids})
            if delete_response.status_code == 200:
                print("Deleted all existing profiles successfully.")
            else:
                print("Failed to delete profiles:", delete_response.text)
        else:
            print("No profiles to delete.")
    else:
        print("Failed to fetch profiles:", response.text)



def update_profile_with_proxy(profile_id, proxy_details=None, args_list=None):
    url = f"{BASE_URL}/browser_profiles/{profile_id}"
    headers = {
        'Authorization': f'Bearer {DOLPHIN_TOKEN}',
        'Content-Type': 'application/json'
    }
    payload = {
        'proxy': proxy_details,
        'args': args_list
    }
    response = requests.patch(url, json=payload, headers=headers)
    return response.json()



def extract_cookies_by_domain(cookies, domain):
    extracted_cookies = []
    for cookie in cookies:
        if cookie.get("domain", "") == f".{domain}":
            extracted_cookies.append(cookie)
    return extracted_cookies


def write_cookies_to_file(cookies, filename):
    with open(filename, 'w') as f:
        json.dump(cookies, f)


def load_cookies_from_file(filename):
    with open(filename, 'r') as f:
        cookies = json.load(f)
    return cookies


def clear_cookies_from_domain(context, domain):
    # Get all cookies
    cookies = context.cookies()

    # Filter cookies by the specified domain
    cookies_to_clear = [cookie for cookie in cookies if domain in cookie['domain']]

    # Clear cookies for the specified domain
    context.clear_cookies()
    context.add_cookies([cookie for cookie in cookies if cookie not in cookies_to_clear])
    print(f"Cleared cookies for domain: {domain}")


def kill_anty_processes():
    try:
        if platform.system() == "Windows":
            # Use taskkill command for Windows
            subprocess.run(["taskkill", "/IM", "anty.exe", "/F"], check=True)
        else:
            # Use pkill command for Unix-based systems
            subprocess.run(["pkill", "anty"], check=True)
        print("Successfully terminated anty processes.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while trying to terminate anty processes: {e}")


def set_cookies(page, cookies):
    context = page.context
    for cookie in cookies:
        if cookie["name"].startswith("__Secure-"):
            cookie["secure"] = True
        context.add_cookies([cookie])
    print("Cookies have been set.")


def get_page_content_with_retry(page, max_retries=5, delay=1):
    for attempt in range(max_retries):
        try:
            content = page.content()
            return content
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(delay)
    raise Exception("Max retries exceeded for getting page content")


def navigate_and_check_url(page, url, max_attempts=5):
    attempt = 0

    while attempt < max_attempts:
        # Navigate to the provided URL
        page.goto(url)
        page.wait_for_load_state("domcontentloaded")
        current_url = page.url

        # Check if "search" is in the URL
        if "store" not in current_url:
            print(f"Attempt {attempt + 1}: 'search' found in URL. Reloading the page.")
            page.reload()
            attempt += 1
            time.sleep(2)  # Add a delay between attempts to allow the page to load properly
        else:
            print("URL check passed.")
            break
    else:
        print("Max attempts reached. 'search' is still in the URL.")


def generate_random_address(address):
    # Generate a random letter
    random_letter = random.choice(string.ascii_lowercase)
    # Generate two random numbers
    random_numbers = ''.join(random.choices(string.digits, k=2))
    # Replace 'k21' with the random letter and numbers
    new_address = address.replace('k21', f'{random_letter}{random_numbers}')
    return new_address
