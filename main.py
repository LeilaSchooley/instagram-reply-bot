import time
import traceback
import time

import pyanty as dolphin
from playwright.sync_api import sync_playwright
from pyanty import DolphinAPI

import openai
import configparser
from playwright.sync_api import sync_playwright

from dolphin import launch_browser, launch_browser_playwright_dolphin
api = DolphinAPI(api_key='eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiNjBmNDAyMTZkNmQ5YjY0NThlNjljZWU4NTFjNGY2YmQzODYyZTI1MTMzYTk2NmQwZjRlMGFiYjEwODA1YWJmZWNhZWYxZDQwOGRjN2UwZDAiLCJpYXQiOjE3MjYwODEwNzcuMjE1OTcxLCJuYmYiOjE3MjYwODEwNzcuMjE1OTczLCJleHAiOjE3Mjg2NzMwNzcuMjAxNDMyLCJzdWIiOiIzNzM4OTQzIiwic2NvcGVzIjpbXX0.UmMdczKsq2wmmAXhGIkFv8LwMaEkDAkZwQvEbinDXhkmUP5Zo_Go3UIs52juMmozzIPUrbSd_fMRcVrw3xAfg-jK2t1VUYUIEeZOADPuovDAC_9ZfFzAyZqpYMd_37fxbd1rSgFMErm8TScTsX7-oHFxgBo2DNCp0-sdcJUrltjyDQGVyr1fo_hdKjSoQ_Jrva4ynDapWT8Xhsl-7sC3eIbYesgunp_q7xxmsgMFGC_HmUsZqAX6rEbFc62X8BtbYRohbtvDlfhKBAuHACTuAK8sd9XBdJG01Hw_pnRhiNAzP7YPqwsnCzqvf7XBLfRnmlHi8KJhnDo4blf277-ouxUNQvssnL1SspsUcL7BDA1gDhQPNbnfPSxxBXhYZxp5EyiULrChcvwIOey-y8HF4SB_CWOE-PKPuPDS3_0wJLacWVrf3FsdD9P5IpVDXXrFWEHFtMCGCkJrPNLB40xoCeCZcHL8S61eI38yhyAfIUWC0Nwi97fuXukUmx7KwjhBUzfjK4nGvNm0h66OdecuMGmw1wqWOc6RVhmvGlzxcMu6xJXpmajOME3LCG6_lm3Nsr1lIlz9OrVcfD044O_NFMkhpslY92x0OcGFCxQWYMOjm2vOpVEUAI8xJ_rU3PI7cHi0dD_wAmQboTtpOycThAMPNF-GnhBBEWxB9SY2aC8')


def type_like_human(page, message, element_selector):
    for char in message:
        page.locator(element_selector).type(char)
        time.sleep(0.05)  # Simulate typing speed


def wait_for_page_load(page, timeout=60000):
    try:
        page.wait_for_load_state("load", timeout=timeout)
        print("Page loaded successfully.")
    except Exception as e:
        pass


class InstagramBot:
    def __init__(self, config_path='config.ini'):
        # Load configuration from config.ini
        self.config = configparser.ConfigParser()
        self.config.read(config_path)

        # OpenAI setup
        openai.api_key = self.config.get("DEFAULT", "OPENAI")

        # Instagram credentials
        self.instagram_username = self.config.get("DEFAULT", "INSTAGRAM_USERNAME")
        self.instagram_password = self.config.get("DEFAULT", "INSTAGRAM_PASS")

    # Function to get the response from OpenAI (ChatGPT)
    def generate_response(self, message):
        response = openai.Completion.create(
            engine="text-davinci-003",  # You can change the model as needed
            prompt=f"Reply to this Instagram message: {message}",
            max_tokens=50
        )
        return response.choices[0].text.strip()

    # Function to simulate typing

    def get_list_items_text(self, page):
        # Query all elements with role="listitem"
        list_items = page.locator('[role="listitem"]')

        # Retrieve all text content from the list items
        list_item_texts = list_items.all_text_contents()

        return list_item_texts, list_items

    def check_inbox_and_reply(self):
        #endpoint, port = launch_browser("456052958")
        profile_id = "456052958"
        profile_response = dolphin.run_profile(profile_id)
        port = profile_response['automation']['port']

        try:
            with sync_playwright() as p:
                browser = p.chromium.connect_over_cdp(f"http://localhost:{port}")

                # Open a new page
                default_context = browser.contexts[0]
                page = default_context.pages[0]

                # Go to Instagram inbox
                #page.goto('https://www.instagram.com/direct/inbox/')
                time.sleep(5)
                list_item_texts, list_items = self.get_list_items_text(page)
                # Print or return the list of text contents
                for index, text in enumerate(list_item_texts):
                    print(f"List Item {index + 1}: {text}")
                while True:
                    for index, text in enumerate(list_item_texts):
                        print(f"List Item {index + 1}: {text}")
                    if "Active" not in text:
                        list_items.nth(index).click()
                        # Wait for the DM page to load and perform necessary actions
                        time.sleep(2)  # Replace with a wait for any action on the DM page

                        # After completing actions on the DM page, go back to the list
                        print("Going back to the list page...")
                        page.go_back()  # This should navigate back to the previous page (list page)

                        # Wait for the list page to fully load before continuing
                        page.wait_for_load_state('load')

                        # Break to refresh the list and continue iterating
                        break

                    # Find messages that are 5 minutes old
                    messages = page.locator('span:has-text("5m")')  # Selector to find messages that are 5 minutes old
                    page.pause()
                    if messages.count() > 0:
                        messages.first.click()
                        time.sleep(2)  # Wait for message to open

                        # Read the last message text
                        last_message = page.locator('div[role="textbox"]').last.text_content()
                        print(f"Last message received: {last_message}")

                        # Send the message to OpenAI to generate a response
                        reply = self.generate_response(last_message)
                        print(f"Reply generated by OpenAI: {reply}")

                        # Type the reply like a human
                        message_input_selector = 'textarea[placeholder="Message..."]'  # Adjust this if the selector changes
                        type_like_human(page, reply, message_input_selector)

                        # Send the message
                        page.locator('button[type="submit"]').click()

                        # Break the loop after responding
                        break
                    else:
                        print("No messages found.")
                    # Wait for some time before checking again
                    time.sleep(60)  # Check every minute

        except:
            traceback.print_exc()
            page.pause()
# Entry point to run the bot
if __name__ == "__main__":
    bot = InstagramBot()
    bot.check_inbox_and_reply()
