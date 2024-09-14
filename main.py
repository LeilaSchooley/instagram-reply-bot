import configparser
import os
import re
import time
import traceback
from openai import OpenAI
import pyanty as dolphin
from playwright.sync_api import sync_playwright
from pyanty import DolphinAPI
from datetime import datetime, timedelta

config_path = os.path.join(os.path.dirname(__file__), "config.ini")
config = configparser.ConfigParser()
config.read(config_path)

DOLPHIN_TOKEN = config.get("DEFAULT", "DOLPHIN_TOKEN")
OPENAI = config.get("DEFAULT", "OPENAI")
api = DolphinAPI(api_key=DOLPHIN_TOKEN)

client = OpenAI(
    # This is the default and can be omitted
    api_key=OPENAI,
)

response_list = []


def type_like_human(text, element):
    # Here `element` is already a Locator object
    for char in text:
        element.type(char)  # Type each character like a human
        time.sleep(0.1)  # Simulate typing delay


def wait_for_page_load(page, timeout=60000):
    try:
        page.wait_for_load_state("load", timeout=timeout)
        #print("Page loaded successfully.")
    except Exception as e:
        pass


def is_last_message_within_5_minutes(last_message_text):
    try:
        # Assuming the last message text includes the time in the format "HH:MM"
        # print(f"Parsing last message time from: {last_message_text}")

        # Split the text to check the time part (we expect something like "14:24")
        time_parts = last_message_text.split()

        # Debugging: Print the split parts to check the content
        # print(f"Split parts of the message: {time_parts}")

        # Ensure we have at least one part and try to extract the time
        if len(time_parts) == 0:
            raise ValueError("Message time format is incorrect")

        # Try to parse the last part of the message as time
        message_time_str = time_parts[-1]  # Get the last part

        # Check if the last part contains ":", which indicates a time
        if ":" not in message_time_str:
            raise ValueError("Time not found in the expected format")

        # Parse the message time
        message_time = datetime.strptime(message_time_str, "%H:%M").time()

        # Get the current time
        current_datetime = datetime.now()

        # Combine today's date with the message time
        message_datetime = datetime.combine(current_datetime.date(), message_time)

        # Calculate the time difference
        time_difference = current_datetime - message_datetime
        time_difference_in_minutes = time_difference.total_seconds() / 60
        print(f"Time difference in minutes: {time_difference_in_minutes}")

        # Check if the time difference is within 5 minutes
        if 5 < time_difference_in_minutes < 6:
            return True
        else:
            return False
    except Exception as e:
        print(f"Error parsing last message time: {e}")
        return False


def get_all_conversation_aria_labels(page):
    # Get all elements that have an aria-label
    all_elements = page.query_selector_all('[aria-label]')

    # Loop through the elements and get the aria-label attribute
    for element in all_elements:
        aria_label = element.get_attribute('aria-label')
        if aria_label and 'Conversation' in aria_label:
            return aria_label


class InstagramBot:
    def __init__(self):
        # Load configuration from config.ini
        pass
        # Instagram credentials
        # self.instagram_username = config.get("DEFAULT", "INSTAGRAM_USERNAME")
        # self.instagram_password = config.get("DEFAULT", "INSTAGRAM_PASS")

    # Function to get the response from OpenAI (ChatGPT)
    def generate_response(self, message):
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Using the chat-based model
            messages=[
                {
                    "role": "user",
                    "content": f"Reply to this Instagram message: {message}",
                }
            ],
            max_tokens=50
        )
        # print(response)
        return response.choices[0].message.content.strip()

    # Function to simulate typing

    def get_list_items_text(self, page):
        # Query all elements with role="listitem"
        list_items = page.locator('[role="listitem"]')

        # Retrieve all text content from the list items
        list_item_texts = list_items.all_text_contents()

        return list_item_texts, list_items



    def get_last_message_text(self, page):
        try:
            # Find and extract the last presentation's text
            presentations = page.locator('[aria-label="Double tap to like"]')

            # Check if presentations are found
            if presentations.count() > 0:
                # Hover over the last presentation to make the "More" button visible
                last_presentation = presentations.nth(presentations.count() - 1)
                last_presentation.hover()

                # Locate the "More" button and click it (ensure it's visible after hovering)
                locator = page.get_by_label("Messages in conversation with").locator("div").filter(
                    has_text=re.compile(r"^More$")).nth(2)

                # Check if the "More" button exists and is visible
                if locator.count() > 0 and locator.is_visible():
                    locator.click()
                    time.sleep(2)  # Allow time for any potential UI updates after clicking "More"

                    # Get the last message's time and text after clicking "More"
                    last_message_time = page.locator(".x1dm5mii > div").first.text_content()
                    last_message_text = last_presentation.text_content().strip()

                    print(f"Last message text: {last_message_text}")
                    print(f"Last message time: {last_message_time}")

                    return last_message_text, last_message_time
                else:
                    print("More button not found or not visible.")
                    return None, None
            else:
                print("No presentations found.")
                return None, None

        except Exception as e:
            print(f"Error fetching last message: {e}")
            return None, None


    def check_inbox_and_reply(self):

        profile_id = "456052958"
        profile_response = dolphin.run_profile(profile_id)
        port = profile_response['automation']['port']
        ws_endpoint = profile_response['automation']['wsEndpoint']
        with (sync_playwright() as p):
            #browser = p.chromium.connect_over_cdp(ws_endpoint)


            browser = p.chromium.connect_over_cdp(f"http://localhost:{port}")

            # Open a new page
            default_context = browser.contexts[0]
            page = default_context.pages[0]

            try:

                # Go to Instagram inbox
                if page.url != "https://www.instagram.com/direct/inbox/":
                    page.goto('https://www.instagram.com/direct/inbox/')
                time.sleep(5)
                #page.pause()
                while True:
                    # list_item_texts, list_items = self.get_list_items_text(page)
                    # for index, text in enumerate(list_item_texts):
                    # Check if "Active" is not in the text
                    # print(f"List Item {index + 1}: {text}")
                    elements = page.query_selector_all('span.x6s0dn4.xzolkzo.x12go9s9.x1rnf11y.xprq8jg.x9f619.x3nfvp2.xl56j7k.x1tu34mt.xdk7pt.x1xc55vz.x1emribx')
                    
                    # Loop through each element and click
                    for element in elements:
                        element.click()
                    # Iterate through the list of text contents
                    # for index, text in enumerate(list_item_texts):
                        # Check if "Active" is not in the text
                        # print(f"List Item {index + 1}: {text}")

                        # if "Active" in text or "5m" in text:
                            # Print the text content of the current list item
                            # print(f"List Item {index + 1}: {list_item_text}")
                            # Click the list item at the current index
                            # list_items.nth(index).click()

                        # Wait for the list page to fully load before continuing
                        wait_for_page_load(page)

                        time.sleep(3)
                        name = get_all_conversation_aria_labels(page)

                        # Check if it's already responded to the users DM
                        if name in response_list:
                            print(f"{name} already in list of replied receipents")
                            continue
                        last_message_text, last_message_time = self.get_last_message_text(page)
                        # print(last_message_time)
                        if not last_message_text and last_message_time:
                            print(f"No message found for {name}")
                            continue

                        if is_last_message_within_5_minutes(last_message_time):
                            # Break to refresh the list and continue iterating
                            print(f"Found message from: {name}, sent within 5 minutes. Replying")


                            # Send the message to OpenAI to generate a response
                            reply = self.generate_response(last_message_text)
                            print(f"Reply generated by OpenAI: {reply}")
                            # Use the 'get_by_label' method to find the message input by its label
                            message_input = page.get_by_label("Message", exact=True)

                            # Fill the message input with the desired text

                            # Type the reply like a human
                            type_like_human(reply, message_input)
                            page.keyboard.press("Enter")
                            print(f"Sent message to {name}")

                            response_list.append(name)
                        else:
                            print(f"Message from : {name} not sent within 5 minutes, continuing")
                            continue
                        # After completing actions on the DM page, go back to the list
                        print("Going back to the list page...")

                        page.go_back()  # This should navigate back to the previous page (list page)


                    else:
                        print("No messages found.")
                    # Wait for some time before checking again
                    time.sleep(10)  # Check every minute

            except:
                traceback.print_exc()
                page.pause()


# Entry point to run the bot
if __name__ == "__main__":
    bot = InstagramBot()
    bot.check_inbox_and_reply()
