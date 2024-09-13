import configparser
import os
import time
import traceback
from openai import OpenAI
import openai
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


def is_last_message_within_5_minutes(last_message_text):
    try:
        # Extract the time part from the last message text (e.g., "23:50")
        message_time_str = last_message_text.split()[1]  # Extracts "23:50" part

        # Get today's date and combine it with the message time
        message_time = datetime.strptime(message_time_str, "%H:%M").time()
        current_time = datetime.now().time()

        # Convert both times to datetime objects for comparison
        today = datetime.now().date()
        message_datetime = datetime.combine(today, message_time)
        current_datetime = datetime.now()

        # Calculate the time difference
        time_difference = current_datetime - message_datetime
        print(f"Time difference: {time_difference}")

        # Check if the time difference is less than or equal to 5 minutes
        if timedelta(minutes=-5) <= time_difference <= timedelta(minutes=5):
            return True
        else:
            return False
    except Exception as e:
        print(f"Error parsing last message time: {e}")
        return False


def get_all_conversation_aria_labels(page):
    # Get all elements that have an aria-label
    all_elements = page.query_selector_all('[aria-label]')

    # List to store the aria-labels containing "Conversation"
    conversation_labels = []

    # Loop through the elements and get the aria-label attribute
    for element in all_elements:
        aria_label = element.get_attribute('aria-label')
        if aria_label and 'Conversation' in aria_label:
            return aria_label


class InstagramBot:
    def __init__(self):
        # Load configuration from config.ini

        # Instagram credentials
        self.instagram_username = config.get("DEFAULT", "INSTAGRAM_USERNAME")
        #self.instagram_password = config.get("DEFAULT", "INSTAGRAM_PASS")

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
        print(response)
        return response.choices[0].message.content.strip()

    # Function to simulate typing

    def get_list_items_text(self, page):
        # Query all elements with role="listitem"
        list_items = page.locator('[role="listitem"]')

        # Retrieve all text content from the list items
        list_item_texts = list_items.all_text_contents()

        return list_item_texts, list_items

    def get_last_message_text(self, page):
        presentations = page.locator('[aria-label="Double tap to like"]')

        # Check if any elements with role="presentation" are found
        count = presentations.count()
        if count > 0:
            # Get the last element's text content
            last_message_text = presentations.nth(count - 1).text_content().strip()
            print(f"Last presentation text: {last_message_text}")

        # Find all elements with data-scope="messages_table"
        messages = page.locator('[data-scope="date_break"]')

        # Check if any elements are found
        count = messages.count()
        if count > 0:
            # Get the last element's text content
            last_message_time = messages.nth(count - 1).text_content()
            print(f"Last message time: {last_message_time}")
            return last_message_time, last_message_time
        else:
            print("No messages found.")
            return None

    def check_inbox_and_reply(self):

        profile_id = "456052958"
        profile_response = dolphin.run_profile(profile_id)
        port = profile_response['automation']['port']

        try:
            with (sync_playwright() as p):
                browser = p.chromium.connect_over_cdp(f"http://localhost:{port}")

                # Open a new page
                default_context = browser.contexts[0]
                page = default_context.pages[0]

                # Go to Instagram inbox
                if page.url != "https://www.instagram.com/direct/inbox/":
                    page.goto('https://www.instagram.com/direct/inbox/')
                time.sleep(5)

                while True:
                    list_item_texts, list_items = self.get_list_items_text(page)
                    for index, text in enumerate(list_item_texts):
                        # Check if "Active" is not in the text
                        print(f"List Item {index + 1}: {text}")

                    # Iterate through the list of text contents
                    for index, text in enumerate(list_item_texts):
                        # Check if "Active" is not in the text
                        print(f"List Item {index + 1}: {text}")

                        if "Active" in text or "5m" in text:
                            # Print the text content of the current list item
                            list_item_text = list_items.nth(index).text_content()  # Correct method to get text
                            print(f"List Item {index + 1}: {list_item_text}")
                            # Click the list item at the current index
                            list_items.nth(index).click()

                            # After completing actions on the DM page, go back to the list
                            print("Going back to the list page...")

                            # Wait for the list page to fully load before continuing
                            wait_for_page_load(page)
                            time.sleep(5)
                            last_message = self.get_last_message_text(page)

                            page.go_back()  # This should navigate back to the previous page (list page)

                            # Break to refresh the list and continue iterating

                            # Read the last message text

                            # Send the message to OpenAI to generate a response
                            reply = self.generate_response(last_message)
                            print(f"Reply generated by OpenAI: {reply}")

                            # Type the reply like a human
                            message_input_selector = 'textarea[placeholder="Message..."]'  # Adjust this if the selector changes
                            type_like_human(page, reply, message_input_selector)
                            page.keyboard.press("Enter")
                            # Send the message

                            # Break the loop after responding
                            break

                        else:

                            print(f"Active found in {text}")

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
