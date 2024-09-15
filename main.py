import configparser
import os
import time
import traceback

import pyanty as dolphin
from openai import OpenAI
from playwright.sync_api import sync_playwright
from pyanty import DolphinAPI

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


def get_all_conversation_aria_labels(page):
    # Get all elements that have an aria-label
    all_elements = page.query_selector_all('[aria-label]')

    # Loop through the elements and get the aria-label attribute
    for element in all_elements:
        aria_label = element.get_attribute('aria-label')
        if aria_label and 'Conversation' in aria_label:
            return aria_label


def generate_response(message):
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


def get_last_message_text(page):
    try:
        # Find and extract the last presentation's text
        presentations = page.locator('[aria-label="Double tap to like"]')

        # Check if presentations are found
        if presentations.count() > 0:
            # Hover over the last presentation to make the "More" button visible
            last_presentation = presentations.nth(presentations.count() - 1)
            last_presentation.hover()
            last_message_text = last_presentation.text_content().strip()

            print(f"Last message text: {last_message_text}")

            return last_message_text
        else:
            print("More button not found or not visible.")
            return None

    except Exception as e:
        print(f"Error fetching last message: {e}")
        return None


def check_inbox_and_reply():
    profile_id = "456052958"
    profile_response = dolphin.run_profile(profile_id)
    port = profile_response['automation']['port']

    with (sync_playwright() as p):

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

                elements = page.locator(".x13dflua")

                # Get the count of matching elements
                count = elements.count()

                # Loop through each element and get its text content
                for i in range(count):
                    element_text = elements.nth(i).text_content()
                    #print(f"Text of element {i + 1}: {element_text}")
                    # Get the main class attribute of the element
                    class_attr = elements.nth(i).get_attribute("class")
                    print(f"{i}: {element_text} | Main class: {class_attr}")

                    # Get all child elements inside this element
                    child_elements = elements.nth(i).locator('*')

                    # Get the count of child elements
                    child_count = child_elements.count()

                    # Loop through each child element and get its class attribute
                    for j in range(child_count):
                        child_class = child_elements.nth(j).get_attribute("class")
                        #print(f"  Child {j + 1}: Class = {child_class}")

                        if child_class is not None and "xzolkzo" in child_class:
                            #print(f"Element {i + 1} has 'xzolkzo' in its class: {class_attr}")
                            print(f"Found new message from user")
                            if "5m" in element_text:
                                element = elements.nth(i)
                                #print(f"Clicking on element {i + 1} that contains '5m'")

                                element.click()

                                # Wait for the list page to fully load before continuing
                                wait_for_page_load(page)

                                time.sleep(3)
                                name = get_all_conversation_aria_labels(page)

                                last_message_text = get_last_message_text(page)

                                # Break to refresh the list and continue iterating
                                print(f"Found message from: {name}, sent within 5 minutes. Replying")

                                # Send the message to OpenAI to generate a response
                                reply = generate_response(last_message_text)
                                print(f"Reply generated by OpenAI: {reply}")
                                # Use the 'get_by_label' method to find the message input by its label
                                message_input = page.get_by_label("Message", exact=True)

                                # Fill the message input with the desired text

                                # Type the reply like a human
                                type_like_human(reply, message_input)
                                page.keyboard.press("Enter")
                                print(f"Sent message to {name}")

                                response_list.append(name)

                    # After completing actions on the DM page, go back to the list
                else:
                    print(elements)
                # Wait for some time before checking again
                time.sleep(45)  # Check every minute

        except:
            traceback.print_exc()
            page.pause()


# Entry point to run the bot
if __name__ == "__main__":
    check_inbox_and_reply()
